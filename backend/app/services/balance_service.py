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
    Returns details: paid, share, net balance.
    """
    members = db.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == group_id).all()
    
    balances = {}
    for member, user in members:
        balances[member.user_id] = {
            "user_id": member.user_id,
            "user_name": user.name,
            "total_paid": Decimal("0"),
            "total_share": Decimal("0"),
            "total_settled": Decimal("0"),  # Positive = Received, Negative = Paid
            "net_balance": Decimal("0"),
        }
    
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    
    for expense in expenses:
        # Skip expenses that are still processing (total_amount is NULL)
        if expense.total_amount is None:
            continue
            
        # Calculate total based on actual splits to ensure system balances (Net = 0)
        # Verify payer exists in group (handle case if payer left but splits remain)
        payer_id = expense.created_by
        
        # We need to sum up all splits for this expense
        expense_total_shares = Decimal("0")
        
        items = db.query(ExpenseItem).filter(ExpenseItem.expense_id == expense.id).all()
        
        for item in items:
            splits = db.query(Split).filter(Split.expense_item_id == item.id).all()
            
            for split in splits:
                if split.user_id in balances:
                    balances[split.user_id]["total_share"] += split.amount
                    balances[split.user_id]["net_balance"] -= split.amount
                    expense_total_shares += split.amount

        # Credit the payer with the EXACT amount that was split among members
        # This ensures Sum(Net Balances) == 0, preventing "phantom debt"
        if payer_id and payer_id in balances:
            balances[payer_id]["total_paid"] += expense_total_shares
            balances[payer_id]["net_balance"] += expense_total_shares
    
    settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
    
    for settlement in settlements:
        if settlement.paid_by in balances:
            balances[settlement.paid_by]["net_balance"] += settlement.amount
            balances[settlement.paid_by]["total_settled"] -= settlement.amount
        
        if settlement.paid_to in balances:
            balances[settlement.paid_to]["net_balance"] -= settlement.amount
            balances[settlement.paid_to]["total_settled"] += settlement.amount
    
    return list(balances.values())


def update_group_balances(db: Session, group_id: uuid.UUID):
    """
    Update the group_balances cache table. 
    """
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


def minimize_debts(balances: list[dict]) -> list[dict]:
    """
    Simplify debts using a greedy algorithm.
    Input balances have 'net_balance' and 'user_name'.
    """
    debtors = []
    creditors = []
    
    for b in balances:
        net = b["net_balance"]
        if net < 0:
            debtors.append({"user_id": b["user_id"], "user_name": b["user_name"], "amount": -net})
        elif net > 0:
            creditors.append({"user_id": b["user_id"], "user_name": b["user_name"], "amount": net})
            
    # Sort by amount descending to greedy match
    debtors.sort(key=lambda x: x["amount"], reverse=True)
    creditors.sort(key=lambda x: x["amount"], reverse=True)
    
    debts = []
    i = 0 # debtor index
    j = 0 # creditor index
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # Amount to settle is min of what debtor owes and creditor is owed
        amount = min(debtor["amount"], creditor["amount"])
        
        if amount > 0:
            debts.append({
                "from_user": debtor["user_name"],
                "to_user": creditor["user_name"],
                "amount": round(amount, 2)
            })
            
        # Update remaining amounts
        debtor["amount"] -= amount
        creditor["amount"] -= amount
        
        # Move indices if settled
        if debtor["amount"] < 0.01:
            i += 1
        if creditor["amount"] < 0.01:
            j += 1
            
    return debts


def calculate_group_debts(db: Session, group_id: uuid.UUID) -> dict:
    """
    Return comprehensive balance view: user stats AND simplified debts.
    """
    balances_list = compute_group_balances(db, group_id)
    debts_list = minimize_debts(balances_list)
    
    return {
        "balances": balances_list,
        "debts": debts_list
    }
