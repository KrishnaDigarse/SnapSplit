"""
API routes for AI-powered bill expense processing.

Endpoints:
- POST /api/v1/expenses/bill - Upload and process bill image (async)
- GET /api/v1/expenses/{expense_id}/status - Poll processing status
"""
import uuid
import os
import logging
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.expense import Expense, SourceType, ExpenseStatus
from app.models.group_member import GroupMember
from app.tasks.ai_tasks import process_bill_image_task
from app.schemas.expense import ExpenseResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["AI Expenses"])

# Configuration
UPLOAD_DIR = "uploads/bills"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("/bill", status_code=status.HTTP_202_ACCEPTED)
async def upload_bill(
    image: Annotated[UploadFile, File(description="Bill image (JPG/PNG, max 10MB)")],
    group_id: Annotated[str, Form(description="Group ID")],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a bill image for asynchronous AI processing.
    
    Process:
    1. Validate user is a member of the group
    2. Validate and save the uploaded image
    3. Create expense with status PROCESSING
    4. Enqueue background task for AI processing
    5. Return immediately
    
    **Note:** This endpoint returns immediately. Use GET /expenses/{id}/status 
    to poll for processing results.
    
    Returns:
        Expense ID and PROCESSING status
    """
    logger.info(f"Bill upload request from user {current_user.id} for group {group_id}")
    
    # Parse and validate group_id
    try:
        group_uuid = uuid.UUID(group_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group_id format"
        )
    
    # Check if user is a member of the group
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_uuid,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
    # Validate file
    if not image.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    file_ext = os.path.splitext(image.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read in chunks to avoid loading entire file in memory)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    # Reset file pointer
    await image.seek(0)
    
    # Read first chunk to check size
    chunk = await image.read(chunk_size)
    file_size = len(chunk)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Create expense with PROCESSING status
    # Leave monetary fields NULL - will be set by AI task
    expense = Expense(
        group_id=group_uuid,
        created_by=current_user.id,
        source_type=SourceType.BILL_IMAGE,
        status=ExpenseStatus.PROCESSING,
        subtotal=None,
        tax=None,
        total_amount=None
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    logger.info(f"Created expense {expense.id} with status PROCESSING")
    
    # Save uploaded file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{expense.id}{file_ext}")
    
    try:
        # Reset file pointer
        await image.seek(0)
        
        # Save file
        with open(file_path, "wb") as f:
            # Write first chunk (already read)
            f.write(chunk)
            
            # Write remaining chunks
            while chunk := await image.read(chunk_size):
                file_size += len(chunk)
                
                if file_size > MAX_FILE_SIZE:
                    # Clean up
                    os.remove(file_path)
                    db.delete(expense)
                    db.commit()
                    
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
                    )
                
                f.write(chunk)
        
        logger.info(f"Saved image to {file_path} ({file_size} bytes)")
        
        # Update expense with image URL
        expense.image_url = f"/{file_path}"
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to save image: {str(e)}")
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(expense)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image"
        )
    
    # Enqueue background task for AI processing
    try:
        task = process_bill_image_task.delay(
            expense_id=str(expense.id),
            image_path=file_path,
            group_id=str(group_uuid)
        )
        
        logger.info(
            f"Enqueued AI processing task {task.id} for expense {expense.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to enqueue task: {str(e)}")
        
        # Mark expense as failed if task enqueue fails
        expense.status = ExpenseStatus.FAILED
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue processing task. Please try again."
        )
    
    # Return immediately with PROCESSING status
    return {
        "id": str(expense.id),
        "status": "PROCESSING",
        "message": "Bill is being processed. Poll /api/v1/expenses/{id}/status for updates.",
        "created_at": expense.created_at.isoformat() if expense.created_at else None
    }


@router.get("/{expense_id}/status")
async def get_expense_status(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the processing status of an expense.
    
    Use this endpoint to poll for the result of async bill processing.
    
    Returns:
        Current status and expense details (if ready)
    """
    # Parse expense_id
    try:
        expense_uuid = uuid.UUID(expense_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid expense_id format"
        )
    
    # Fetch expense
    expense = db.query(Expense).filter(Expense.id == expense_uuid).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Check authorization - user must be a member of the group
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == expense.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this expense"
        )
    
    # Return status with appropriate details
    response = {
        "expense_id": str(expense.id),
        "status": expense.status.value,
        "created_at": expense.created_at.isoformat() if expense.created_at else None
    }
    
    # Add details if processing is complete
    if expense.status == ExpenseStatus.READY:
        response.update({
            "subtotal": str(expense.subtotal) if expense.subtotal else None,
            "tax": str(expense.tax) if expense.tax else None,
            "total_amount": str(expense.total_amount) if expense.total_amount else None,
            "items_count": len(expense.items) if expense.items else 0
        })
    elif expense.status == ExpenseStatus.FAILED:
        response.update({
            "error_message": "AI processing failed. Please try uploading the image again."
        })
    
    return response

