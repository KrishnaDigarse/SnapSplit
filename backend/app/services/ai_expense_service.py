"""
AI-powered expense service for processing bill images.

This service orchestrates the AI pipeline:
1. OCR text extraction
2. LLM structured data extraction
3. Data validation and cleanup
4. Expense creation with items and splits
"""
import logging
import os
import uuid
from typing import Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from app.ai.ocr import extract_text_from_image, OCRError
from app.ai.llm import extract_bill_data, LLMError
from app.ai.parser import validate_bill_data, ValidationError
from app.models.expense import Expense, ExpenseStatus, SourceType
from app.models.expense_item import ExpenseItem
from app.models.split import Split, SplitType
from app.models.group_member import GroupMember
from app.services.balance_service import update_group_balances

logger = logging.getLogger(__name__)


class AIProcessingError(Exception):
    """Raised when AI processing fails."""
    pass


def process_bill_image(
    db: Session,
    expense_id: uuid.UUID,
    image_path: str,
    group_id: uuid.UUID
) -> Expense:
    """
    Process a bill image through the AI pipeline and update expense.
    
    Pipeline:
    1. Extract text via OCR
    2. Extract structured data via LLM
    3. Validate and clean data
    4. Create expense items
    5. Generate equal splits
    6. Update balances
    7. Mark expense as READY
    
    Args:
        db: Database session
        expense_id: ID of the expense to update
        image_path: Path to the uploaded bill image
        group_id: ID of the group
        
    Returns:
        Updated expense with status READY or FAILED
        
    Note:
        This function NEVER raises exceptions. It always returns an expense
        with either READY or FAILED status. Errors are logged and stored.
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        logger.error(f"Expense {expense_id} not found")
        raise ValueError(f"Expense {expense_id} not found")
    
    try:
        logger.info(f"Starting AI processing for expense {expense_id}")
        
        # Step 1: OCR text extraction
        logger.info("Step 1: Extracting text via OCR")
        try:
            ocr_text = extract_text_from_image(image_path)
            expense.raw_ocr_text = ocr_text
            db.commit()
            logger.info(f"OCR extracted {len(ocr_text)} characters")
        except OCRError as e:
            logger.error(f"OCR failed: {str(e)}")
            _mark_expense_failed(db, expense, f"OCR failed: {str(e)}")
            return expense
        
        # Step 2: LLM structured data extraction
        logger.info("Step 2: Extracting structured data via LLM")
        try:
            bill_data = extract_bill_data(ocr_text)
            logger.info(f"LLM extracted {len(bill_data.get('items', []))} items")
        except LLMError as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            _mark_expense_failed(db, expense, f"LLM extraction failed: {str(e)}")
            return expense
        
        # Step 3: Validate and clean data
        logger.info("Step 3: Validating and cleaning data")
        try:
            validated_data = validate_bill_data(bill_data)
            logger.info("Data validation successful")
        except ValidationError as e:
            logger.error(f"Validation failed: {str(e)}")
            _mark_expense_failed(db, expense, f"Validation failed: {str(e)}")
            return expense
        
        # Step 4: Create expense items
        logger.info("Step 4: Creating expense items")
        expense_items = _create_expense_items(db, expense_id, validated_data['items'])
        logger.info(f"Created {len(expense_items)} expense items")
        
        # Step 5: Generate equal splits for all group members
        logger.info("Step 5: Generating equal splits")
        splits = _create_equal_splits(db, expense_items, group_id)
        logger.info(f"Created {len(splits)} splits")
        
        # Step 6: Update expense totals
        logger.info("Step 6: Updating expense totals")
        expense.subtotal = validated_data['subtotal']
        expense.tax = validated_data['tax']
        expense.total_amount = validated_data['total']
        expense.status = ExpenseStatus.READY
        db.commit()
        
        # Step 7: Update group balances
        logger.info("Step 7: Updating group balances")
        update_group_balances(db, group_id)
        
        logger.info(f"AI processing completed successfully for expense {expense_id}")
        return expense
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in AI processing: {str(e)}", exc_info=True)
        _mark_expense_failed(db, expense, f"Unexpected error: {str(e)}")
        return expense


def _create_expense_items(
    db: Session,
    expense_id: uuid.UUID,
    items_data: list
) -> list[ExpenseItem]:
    """
    Create expense items from validated data.
    
    Args:
        db: Database session
        expense_id: Parent expense ID
        items_data: List of item dictionaries
        
    Returns:
        List of created ExpenseItem objects
    """
    expense_items = []
    
    for item_data in items_data:
        expense_item = ExpenseItem(
            expense_id=expense_id,
            item_name=item_data['name'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.add(expense_item)
        expense_items.append(expense_item)
    
    db.commit()
    
    # Refresh to get IDs
    for item in expense_items:
        db.refresh(item)
    
    return expense_items


def _create_equal_splits(
    db: Session,
    expense_items: list[ExpenseItem],
    group_id: uuid.UUID
) -> list[Split]:
    """
    Create equal splits for all group members across all items.
    
    Args:
        db: Database session
        expense_items: List of expense items
        group_id: Group ID
        
    Returns:
        List of created Split objects
    """
    # Get all group members
    members = db.query(GroupMember).filter(
        GroupMember.group_id == group_id
    ).all()
    
    if not members:
        raise ValueError(f"No members found in group {group_id}")
    
    member_count = len(members)
    splits = []
    
    # Create equal splits for each item
    for expense_item in expense_items:
        total_item_cost = Decimal(str(expense_item.price)) * expense_item.quantity
        split_amount = (total_item_cost / member_count).quantize(Decimal('0.01'))
        
        for member in members:
            split = Split(
                expense_item_id=expense_item.id,
                user_id=member.user_id,
                amount=split_amount,
                split_type=SplitType.EQUAL
            )
            db.add(split)
            splits.append(split)
    
    db.commit()
    
    return splits


def _mark_expense_failed(db: Session, expense: Expense, error_message: str) -> None:
    """
    Mark expense as FAILED and store error message.
    
    Args:
        db: Database session
        expense: Expense object
        error_message: Error description
    """
    expense.status = ExpenseStatus.FAILED
    db.commit()
    logger.info(f"Marked expense {expense.id} as FAILED: {error_message}")
