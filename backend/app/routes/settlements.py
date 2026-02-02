from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.settlement import SettlementCreate, SettlementResponse, GroupFinancialsResponse
from app.services import settlement_service
from typing import List
import uuid

router = APIRouter(prefix="/settlements", tags=["Settlements"])


@router.post("", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
def create_settlement(
    settlement_data: SettlementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a settlement (partial payment allowed)"""
    return settlement_service.create_settlement(db, current_user, settlement_data)


@router.get("/balances/{group_id}", response_model=GroupFinancialsResponse)
def get_group_balances(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get balances and simplified debts for a group"""
    return settlement_service.get_group_financials(db, current_user, group_id)
