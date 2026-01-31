import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Numeric, String, DateTime, Enum as SQLEnum
from app.models.types import GUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK = "BANK"
    OTHER = "OTHER"


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    group_id = Column(GUID, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    paid_by = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    paid_to = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    group = relationship("Group", back_populates="settlements")
    payer = relationship("User", foreign_keys=[paid_by], back_populates="settlements_paid")
    payee = relationship("User", foreign_keys=[paid_to], back_populates="settlements_received")

    def __repr__(self):
        return f"<Settlement(id={self.id}, amount={self.amount}, method={self.payment_method})>"
