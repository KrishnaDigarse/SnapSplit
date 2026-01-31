import uuid
from sqlalchemy import Column, ForeignKey, Numeric, Enum as SQLEnum
from app.models.types import GUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class SplitType(str, enum.Enum):
    EQUAL = "EQUAL"
    ITEM = "ITEM"
    CUSTOM = "CUSTOM"


class Split(Base):
    __tablename__ = "splits"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    expense_item_id = Column(GUID, ForeignKey("expense_items.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    split_type = Column(SQLEnum(SplitType), nullable=False)

    # Relationships
    expense_item = relationship("ExpenseItem", back_populates="splits")
    user = relationship("User", back_populates="splits")

    def __repr__(self):
        return f"<Split(id={self.id}, user={self.user_id}, amount={self.amount}, type={self.split_type})>"
