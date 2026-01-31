import uuid
from sqlalchemy import Column, ForeignKey, String, Integer, Numeric
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    expense_id = Column(GUID, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    expense = relationship("Expense", back_populates="items")
    splits = relationship("Split", back_populates="expense_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExpenseItem(id={self.id}, name={self.item_name}, price={self.price})>"
