import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
import uuid

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.database import Base
from app.models.user import User
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.expense import Expense
from app.models.expense_item import ExpenseItem
from app.models.split import Split
from app.services.balance_service import calculate_group_debts, compute_group_balances

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./snapsplit.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

GROUP_ID = uuid.UUID("28c9e60d-e65e-4fed-b938-3186f62e9882")

def debug_group():
    print(f"\n--- Debugging Group {GROUP_ID} ---")
    
    members = db.query(GroupMember, User).join(User, GroupMember.user_id == User.id).filter(GroupMember.group_id == GROUP_ID).all()
    balances = {}
    for member, user in members:
        print(f"Member ID type: {type(member.user_id)} - {member.user_id}")
        balances[member.user_id] = {"net": Decimal(0), "name": user.name}

    expenses = db.query(Expense).filter(Expense.group_id == GROUP_ID).all()
    
    for expense in expenses:
        if expense.total_amount is None: continue
        
        print(f"\nProcessing Expense {expense.id} (Total: {expense.total_amount})")
        print(f"  Created By: {expense.created_by} (Type: {type(expense.created_by)})")
        
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        print(f"  Items ({len(items)}):")
        item_sum = Decimal(0)
        for i in items:
            print(f"    - {i.item_name}: {i.price} (Qty: {i.quantity}) ID: {i.id}")
            item_sum += (i.price * i.quantity)
        print(f"  Item Sum: {item_sum} vs Total: {expense.total_amount}")
        
        # Credit Payer
        if expense.created_by in balances:
            balances[expense.created_by]["net"] += expense.total_amount
            print(f"  [CREDIT] Added {expense.total_amount} to {balances[expense.created_by]['name']}")
        else:
            print(f"  [ERROR] Creator {expense.created_by} not found in balances keys: {list(balances.keys())}")

        # Debit Splitters
        for item in expense.items:
            splits = db.query(Split).filter(Split.expense_item_id == item.id).all()
            for split in splits:
                if split.user_id in balances:
                    balances[split.user_id]["net"] -= split.amount
                    print(f"  [DEBIT] Subtracted {split.amount} from {balances[split.user_id]['name']}")
                else:
                     print(f"  [ERROR] Split User {split.user_id} not found in balances keys")

    print("\nFinal Balances:")
    for uid, data in balances.items():
        print(f"{data['name']}: {data['net']}")

if __name__ == "__main__":
    debug_group()
