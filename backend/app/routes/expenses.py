from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense import ManualExpenseCreate, ExpenseResponse, ExpenseDetailResponse, ExpenseUpdate
from app.services import expense_service
from typing import List
import uuid

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/manual", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_manual_expense(
    expense_data: ManualExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a manual expense"""
    return expense_service.create_manual_expense(db, current_user, expense_data)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expense details"""
    return expense_service.get_expense(db, current_user, expense_id)


@router.get("/group/{group_id}", response_model=List[ExpenseResponse])
def get_group_expenses(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for a group"""
    return expense_service.get_group_expenses(db, current_user, group_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: uuid.UUID,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    return expense_service.update_expense(db, current_user, expense_id, expense_data)
