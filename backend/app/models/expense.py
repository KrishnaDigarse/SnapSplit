import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Numeric, Text, Enum as SQLEnum
from app.models.types import GUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class SourceType(str, enum.Enum):
    BILL_IMAGE = "BILL_IMAGE"
    MANUAL = "MANUAL"


class ExpenseStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    group_id = Column(GUID, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    image_url = Column(String(500), nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    status = Column(SQLEnum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=True)  # NULL during PROCESSING
    tax = Column(Numeric(10, 2), default=0, nullable=True)  # NULL during PROCESSING
    total_amount = Column(Numeric(10, 2), nullable=True)  # NULL during PROCESSING
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    group = relationship("Group", back_populates="expenses")
    creator = relationship("User", back_populates="expenses_created")
    items = relationship("ExpenseItem", back_populates="expense", cascade="all, delete-orphan")

    @property
    def creator_name(self):
        return self.creator.name if self.creator else None

    def __repr__(self):
        return f"<Expense(id={self.id}, total={self.total_amount}, status={self.status})>"
