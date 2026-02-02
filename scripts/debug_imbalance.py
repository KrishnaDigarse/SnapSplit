from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.expense import Expense
from app.models.expense_item import ExpenseItem
from app.models.split import Split
from app.models.group_member import GroupMember
from app.models.user import User
import os

# Setup DB connection
# Use absolute path for reliability
SQLALCHEMY_DATABASE_URL = "sqlite:///c:/Users/krish/Documents/Project/SnapSplit/backend/sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def analyze_imbalance():
    # Find the group (assuming there's only one relevant group or we pick the first one)
    # Or iterate all groups
    expenses = db.query(Expense).all()
    
    print(f"Analyzing {len(expenses)} expenses...")
    
    total_imbalance = 0
    
    for expense in expenses:
        if expense.total_amount is None:
            continue
            
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        split_sum = 0
        for item in items:
            splits = db.query(Split).filter(Split.expense_item_id == item.id).all()
            for split in splits:
                split_sum += split.amount
        
        diff = split_sum - expense.total_amount
        if abs(diff) > 0.01:
            print(f"Expense {expense.id} ({expense.description}): Total {expense.total_amount} vs Splits {split_sum} (Diff: {diff})")
            total_imbalance += diff
            
    print(f"Total Imbalance in system: {total_imbalance}")

if __name__ == "__main__":
    analyze_imbalance()
