"""
Background tasks for AI bill processing.

This module contains Celery tasks that run asynchronously to process bill images.
Tasks are retried automatically on transient failures.
"""
import logging
import uuid
from typing import Optional
from celery import Task
from celery.exceptions import Retry
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.expense import Expense, ExpenseStatus
from app.services.ai_expense_service import process_bill_image, AIProcessingError
from app.ai.ocr import OCRError
from app.ai.llm import LLMError
from app.ai.parser import ValidationError

logger = logging.getLogger(__name__)


class AIProcessingTask(Task):
    """
    Base task class for AI processing with custom error handling.
    """
    autoretry_for = (OCRError, LLMError, ConnectionError, TimeoutError)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 300  # 5 minutes max
    retry_jitter = True


@celery_app.task(
    bind=True,
    base=AIProcessingTask,
    name="app.tasks.ai_tasks.process_bill_image_task",
    retry_backoff=30,  # Start with 30s
    retry_backoff_max=300,  # Max 300s (5 minutes)
    max_retries=3,
    autoretry_for=(OCRError, LLMError, ConnectionError, TimeoutError),
    dont_autoretry_for=(ValidationError, ValueError, FileNotFoundError)
)
def process_bill_image_task(
    self,
    expense_id: str,
    image_path: str,
    group_id: str
) -> dict:
    """
    Process a bill image asynchronously using AI pipeline.
    
    This task:
    1. Checks idempotency (prevents double-processing)
    2. Runs OCR to extract text
    3. Uses LLM to parse structured data
    4. Validates and cleans the data
    5. Creates expense items and splits
    6. Updates expense status to READY or FAILED
    
    Args:
        expense_id: UUID of the expense to process
        image_path: Path to the uploaded bill image
        group_id: UUID of the group this expense belongs to
        
    Returns:
        dict: Processing result with status and message
        
    Raises:
        Retry: On transient errors (OCR, LLM, network)
        
    Note:
        This task is idempotent - it will not reprocess an expense
        that has already been processed (status != PROCESSING).
    """
    db: Optional[Session] = None
    
    try:
        # Convert string UUIDs back to UUID objects
        expense_uuid = uuid.UUID(expense_id)
        group_uuid = uuid.UUID(group_id)
        
        # Create database session
        db = SessionLocal()
        
        # Fetch expense
        expense = db.query(Expense).filter(Expense.id == expense_uuid).first()
        
        if not expense:
            logger.error(f"Expense {expense_id} not found")
            return {
                "status": "error",
                "message": f"Expense {expense_id} not found"
            }
        
        # IDEMPOTENCY GUARD: Check if already processed
        if expense.status != ExpenseStatus.PROCESSING:
            logger.warning(
                f"Expense {expense_id} already processed (status: {expense.status}). "
                "Skipping to prevent double-processing."
            )
            return {
                "status": "skipped",
                "message": f"Expense already in {expense.status} state",
                "expense_id": expense_id
            }
        
        logger.info(f"Starting AI processing for expense {expense_id}")
        
        # Process bill image through AI pipeline
        updated_expense = process_bill_image(
            db=db,
            expense_id=expense_uuid,
            image_path=image_path,
            group_id=group_uuid
        )
        
        db.commit()
        
        logger.info(
            f"Successfully processed expense {expense_id}: "
            f"{len(updated_expense.items)} items, total: {updated_expense.total_amount}"
        )
        
        return {
            "status": "success",
            "message": "Bill processed successfully",
            "expense_id": expense_id,
            "items_count": len(updated_expense.items),
            "total_amount": str(updated_expense.total_amount)
        }
        
    except (OCRError, LLMError, ConnectionError, TimeoutError) as e:
        # Transient errors - retry
        logger.warning(
            f"Transient error processing expense {expense_id} "
            f"(attempt {self.request.retries + 1}/3): {str(e)}"
        )
        
        # Mark as failed if max retries exceeded
        if self.request.retries >= self.max_retries:
            if db and expense:
                expense.status = ExpenseStatus.FAILED
                db.commit()
                logger.error(f"Max retries exceeded for expense {expense_id}. Marked as FAILED.")
        
        # Retry with exponential backoff (30s, 90s, 300s)
        raise self.retry(exc=e, countdown=30 * (3 ** self.request.retries))
        
    except (ValidationError, ValueError, FileNotFoundError) as e:
        # Permanent errors - don't retry
        logger.error(f"Permanent error processing expense {expense_id}: {str(e)}")
        
        if db and expense:
            expense.status = ExpenseStatus.FAILED
            db.commit()
        
        return {
            "status": "failed",
            "message": str(e),
            "expense_id": expense_id
        }
        
    except Exception as e:
        # Unexpected errors - log and mark as failed
        logger.exception(f"Unexpected error processing expense {expense_id}: {str(e)}")
        
        if db and expense:
            expense.status = ExpenseStatus.FAILED
            db.commit()
        
        return {
            "status": "failed",
            "message": f"Unexpected error: {str(e)}",
            "expense_id": expense_id
        }
        
    finally:
        # Always close database session
        if db:
            db.close()
