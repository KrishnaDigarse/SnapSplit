from pydantic import BaseModel, UUID4, field_validator
from datetime import datetime
from decimal import Decimal
from app.models.settlement import PaymentMethod


class SettlementCreate(BaseModel):
    group_id: UUID4
    paid_to: UUID4
    amount: Decimal
    payment_method: PaymentMethod = PaymentMethod.CASH
    note: str | None = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class SettlementResponse(BaseModel):
    id: UUID4
    group_id: UUID4
    paid_by: UUID4
    paid_to: UUID4
    amount: Decimal
    payment_method: PaymentMethod
    note: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupBalanceResponse(BaseModel):
    user_id: UUID4
    user_name: str
    net_balance: Decimal
    updated_at: datetime
