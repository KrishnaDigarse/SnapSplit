from pydantic import BaseModel, UUID4, field_validator
from datetime import datetime
from typing import List
from decimal import Decimal
from app.models.split import SplitType


class ExpenseItemCreate(BaseModel):
    item_name: str
    quantity: int = 1
    price: Decimal


class SplitCreate(BaseModel):
    user_id: UUID4
    amount: Decimal
    split_type: SplitType = SplitType.EQUAL


class ManualExpenseCreate(BaseModel):
    group_id: UUID4
    items: List[ExpenseItemCreate]
    splits: List[SplitCreate]
    subtotal: Decimal
    tax: Decimal = Decimal("0")
    total_amount: Decimal
    
    @field_validator('total_amount')
    @classmethod
    def validate_total(cls, v, info):
        if 'subtotal' in info.data and 'tax' in info.data:
            expected_total = info.data['subtotal'] + info.data['tax']
            if abs(v - expected_total) > Decimal("0.01"):
                raise ValueError("total_amount must equal subtotal + tax")
        return v


class ExpenseItemResponse(BaseModel):
    id: UUID4
    expense_id: UUID4
    item_name: str
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True


class SplitResponse(BaseModel):
    id: UUID4
    expense_item_id: UUID4
    user_id: UUID4
    amount: Decimal
    split_type: SplitType
    
    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    id: UUID4
    group_id: UUID4
    created_by: UUID4 | None
    source_type: str
    status: str
    is_edited: bool
    subtotal: Decimal
    tax: Decimal
    total_amount: Decimal
    created_at: datetime
    items: List[ExpenseItemResponse] = []
    raw_ocr_text: str | None = None  # For debugging AI pipeline
    
    class Config:
        from_attributes = True


class ExpenseDetailResponse(ExpenseResponse):
    splits: List[SplitResponse] = []
