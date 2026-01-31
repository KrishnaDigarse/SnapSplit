from datetime import datetime
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, PrimaryKeyConstraint, Index
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class GroupBalance(Base):
    __tablename__ = "group_balances"

    group_id = Column(GUID, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    net_balance = Column(Numeric(10, 2), default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("group_id", "user_id"),
        Index("idx_group_balances_group_id", "group_id"),
        Index("idx_group_balances_user_id", "user_id"),
    )

    # Relationships
    group = relationship("Group", back_populates="balances")
    user = relationship("User", back_populates="group_balances")

    def __repr__(self):
        return f"<GroupBalance(group={self.group_id}, user={self.user_id}, balance={self.net_balance})>"
