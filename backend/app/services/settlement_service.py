from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.settlement import Settlement
from app.models.group_member import GroupMember
from app.models.group_balance import GroupBalance
from app.schemas.settlement import SettlementCreate
from typing import List
import uuid


def create_settlement(db: Session, current_user: User, settlement_data: SettlementCreate) -> Settlement:
    """Create a settlement (partial payment)"""
    if current_user.id == settlement_data.paid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay yourself"
        )
    
    is_payer_member = db.query(GroupMember).filter(
        GroupMember.group_id == settlement_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    is_payee_member = db.query(GroupMember).filter(
        GroupMember.group_id == settlement_data.group_id,
        GroupMember.user_id == settlement_data.paid_to
    ).first()
    
    if not is_payer_member or not is_payee_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both users must be members of the group"
        )
    
    settlement = Settlement(
        group_id=settlement_data.group_id,
        paid_by=current_user.id,
        paid_to=settlement_data.paid_to,
        amount=settlement_data.amount,
        payment_method=settlement_data.payment_method,
        note=settlement_data.note
    )
    
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    
    from app.services.balance_service import update_group_balances
    update_group_balances(db, settlement_data.group_id)
    
    return settlement


def get_group_balances(db: Session, current_user: User, group_id: uuid.UUID) -> List[dict]:
    """Get balances for all members in a group"""
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    from app.services.balance_service import compute_group_balances
    return compute_group_balances(db, group_id)
