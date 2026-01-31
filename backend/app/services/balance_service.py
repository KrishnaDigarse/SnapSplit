from sqlalchemy.orm import Session
from app.models.group_member import GroupMember
from app.models.group_balance import GroupBalance
from app.models.split import Split
from app.models.settlement import Settlement
from app.models.expense_item import ExpenseItem
from app.models.expense import Expense
from app.models.user import User
from decimal import Decimal
from datetime import datetime
import uuid


def compute_group_balances(db: Session, group_id: uuid.UUID) -> list[dict]:
    """
    Compute net balance for each user in a group.
    Positive balance = user is owed money
    Negative balance = user owes money
    """
    members = db.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == group_id).all()
    
    balances = {}
    for member, user in members:
        balances[member.user_id] = {
            "user_id": member.user_id,
            "user_name": user.name,
            "net_balance": Decimal("0"),
            "updated_at": datetime.utcnow()
        }
    
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    
    for expense in expenses:
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        
        for item in items:
            splits = db.query(Split).filter(Split.expense_item_id == item.id).all()
            
            for split in splits:
                if split.user_id in balances:
                    balances[split.user_id]["net_balance"] -= split.amount
        
        if expense.created_by and expense.created_by in balances:
            balances[expense.created_by]["net_balance"] += expense.total_amount
    
    settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
    
    for settlement in settlements:
        if settlement.paid_by in balances:
            balances[settlement.paid_by]["net_balance"] -= settlement.amount
        
        if settlement.paid_to in balances:
            balances[settlement.paid_to]["net_balance"] += settlement.amount
    
    return list(balances.values())


def update_group_balances(db: Session, group_id: uuid.UUID):
    """Update the group_balances cache table"""
    computed_balances = compute_group_balances(db, group_id)
    
    for balance_data in computed_balances:
        existing_balance = db.query(GroupBalance).filter(
            GroupBalance.group_id == group_id,
            GroupBalance.user_id == balance_data["user_id"]
        ).first()
        
        if existing_balance:
            existing_balance.net_balance = balance_data["net_balance"]
            existing_balance.updated_at = datetime.utcnow()
        else:
            new_balance = GroupBalance(
                group_id=group_id,
                user_id=balance_data["user_id"],
                net_balance=balance_data["net_balance"],
                updated_at=datetime.utcnow()
            )
            db.add(new_balance)
    
    db.commit()
