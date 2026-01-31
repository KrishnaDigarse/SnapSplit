from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.expense import Expense, SourceType, ExpenseStatus
from app.models.expense_item import ExpenseItem
from app.models.split import Split
from app.models.group_member import GroupMember
from app.schemas.expense import ManualExpenseCreate
from typing import List
from decimal import Decimal
import uuid


def create_manual_expense(db: Session, current_user: User, expense_data: ManualExpenseCreate) -> Expense:
    """Create a manual expense with items and splits"""
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == expense_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    split_total = sum(split.amount for split in expense_data.splits)
    if abs(split_total - expense_data.total_amount) > Decimal("0.01"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Split amounts ({split_total}) must equal total amount ({expense_data.total_amount})"
        )
    
    expense = Expense(
        group_id=expense_data.group_id,
        created_by=current_user.id,
        source_type=SourceType.MANUAL,
        status=ExpenseStatus.READY,
        is_edited=False,
        subtotal=expense_data.subtotal,
        tax=expense_data.tax,
        total_amount=expense_data.total_amount
    )
    
    db.add(expense)
    db.flush()
    
    for item_data in expense_data.items:
        item = ExpenseItem(
            expense_id=expense.id,
            item_name=item_data.item_name,
            quantity=item_data.quantity,
            price=item_data.price
        )
        db.add(item)
    
    db.flush()
    
    first_item = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).first()
    
    for split_data in expense_data.splits:
        is_split_member = db.query(GroupMember).filter(
            GroupMember.group_id == expense_data.group_id,
            GroupMember.user_id == split_data.user_id
        ).first()
        
        if not is_split_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {split_data.user_id} is not a member of the group"
            )
        
        split = Split(
            expense_item_id=first_item.id,
            user_id=split_data.user_id,
            amount=split_data.amount,
            split_type=split_data.split_type
        )
        db.add(split)
    
    db.commit()
    db.refresh(expense)
    
    from app.services.balance_service import update_group_balances
    update_group_balances(db, expense_data.group_id)
    
    return expense


def get_expense(db: Session, current_user: User, expense_id: uuid.UUID) -> Expense:
    """Get expense details"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == expense.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this expense"
        )
    
    return expense


def get_group_expenses(db: Session, current_user: User, group_id: uuid.UUID) -> List[Expense]:
    """Get all expenses for a group"""
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    expenses = db.query(Expense).filter(Expense.group_id == group_id).order_by(Expense.created_at.desc()).all()
    return expenses
