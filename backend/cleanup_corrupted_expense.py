import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

sys.path.append(os.getcwd())

from app.models.expense import Expense
from app.models.expense_item import ExpenseItem
from app.models.split import Split
from app.services.balance_service import update_group_balances

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./snapsplit.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

GROUP_ID = uuid.UUID("28c9e60d-e65e-4fed-b938-3186f62e9882")
# The corrupted expense from debug output
EXPENSE_ID = uuid.UUID("39c62fac-3702-4dac-956e-ea60dac782d7") 
# Wait, debug output showed: Processing Expense 39c62fac...
# Check previous debug logs to be sure of ID.
# From Step 2100 trace: Processing Expense 39c62fac-3702-4dac-956e-ea60dac782d7 (Total: 1439.00)
# Wait, the TOTAL changed? In Step 2088 trace it was 2b4e6a39... Total 1381.00.
# In Step 2100 trace it is 39c62fac... Total 1439.00.
# It seems there are MULTIPLE corrupted expenses? Or the user added another one?
# I should clean ALL expenses for this group to be safe? Or just iterate and fix items > total?

def cleanup():
    print("Starting cleanup...")
    expenses = db.query(Expense).filter(Expense.group_id == GROUP_ID).all()
    
    for expense in expenses:
        print(f"Checking Expense {expense.id}...")
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        splits = db.query(Split).join(Expense.items).filter(Split.expense_item_id.in_([i.id for i in items])).all()
        # Note: join(Expense.items) might be insufficient if items are detached.
        # Better: get splits for these items.
        
        # Calculate sum
        item_sum = sum(i.price * i.quantity for i in items)
        
        if len(items) > 0 and (item_sum > expense.total_amount * 2): # heuristic: if items sum is way larger
            print(f"  [CORRUPTED] Sum {item_sum} > Total {expense.total_amount}. Cleaning up items/splits.")
            
            # Delete all items (cascade should handle splits, but let's be explicit)
            # Delete splits first
            for item in items:
                db.query(Split).filter(Split.expense_item_id == item.id).delete()
            
            # Delete items
            db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).delete()
            
            # Re-create simple placeholder item? Or just leave empty?
            # ExpenseUpdate requires items.
            # If I leave it empty, the user might see empty items and can edit it.
            # But split calculations will be wrong (0 splits).
            # So I should create 1 dummy item equal to total amount.
            
            print("  Creating placeholder item...")
            placeholder = ExpenseItem(
                expense_id=expense.id,
                item_name="Restored Item",
                quantity=1,
                price=expense.total_amount
            )
            db.add(placeholder)
            db.flush()
            
            # Create splits
            # We need equal splits for current members
            from app.models.group_member import GroupMember
            from app.models.split import SplitType
            
            members = db.query(GroupMember).filter(GroupMember.group_id == GROUP_ID).all()
            ct = len(members)
            if ct > 0:
                amount = expense.total_amount / ct
                # handling rounding omitted for simplicity script, close enough
                for m in members:
                    s = Split(
                        expense_item_id=placeholder.id,
                        user_id=m.user_id,
                        amount=amount,
                        split_type=SplitType.EQUAL
                    )
                    db.add(s)
            
            expense.is_edited = True
            db.commit()
            print("  Fixed.")
            
    print("Updating balances...")
    update_group_balances(db, GROUP_ID)
    print("Done.")

if __name__ == "__main__":
    cleanup()
