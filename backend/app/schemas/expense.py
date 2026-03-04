from pydantic import BaseModel, UUID4, field_validator
from datetime import datetime
from typing import List
from decimal import Decimal
from app.models.split import SplitType


class ExpenseItemCreate(BaseModel):
    item_name: str
    quantity: int = 1
    price: Decimal
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        if v > Decimal('1000000'):
            raise ValueError('Price exceeds maximum allowed value ($1,000,000)')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 10000:
            raise ValueError('Quantity exceeds maximum allowed value (10,000)')
        return v


class SplitCreate(BaseModel):
    user_id: UUID4
    amount: Decimal
    split_type: SplitType = SplitType.EQUAL
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Split amount cannot be negative')
        if v > Decimal('1000000'):
            raise ValueError('Split amount exceeds maximum allowed value ($1,000,000)')
        return v


class ManualExpenseCreate(BaseModel):
    group_id: UUID4
    items: List[ExpenseItemCreate]
    splits: List[SplitCreate]
    subtotal: Decimal
    tax: Decimal = Decimal("0")
    total_amount: Decimal
    
    @field_validator('subtotal', 'total_amount')
    @classmethod
    def validate_amounts(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > Decimal('1000000'):
            raise ValueError('Amount exceeds maximum allowed value ($1,000,000)')
        return v
    
    @field_validator('tax')
    @classmethod
    def validate_tax(cls, v):
        if v < 0:
            raise ValueError('Tax cannot be negative')
        if v > Decimal('100000'):
            raise ValueError('Tax exceeds maximum allowed value ($100,000)')
        return v
    
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
    creator_name: str | None = None
    source_type: str
    status: str
    is_edited: bool
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total_amount: Decimal | None = None
    created_at: datetime
    items: List[ExpenseItemResponse] = []
    raw_ocr_text: str | None = None  # For debugging AI pipeline
    
    class Config:
        from_attributes = True


class ExpenseDetailResponse(ExpenseResponse):
    splits: List[SplitResponse] = []


class ExpenseUpdate(BaseModel):
    description: str | None = None
    items: List[ExpenseItemCreate]
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
