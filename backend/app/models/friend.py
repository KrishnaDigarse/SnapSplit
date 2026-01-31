from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, PrimaryKeyConstraint, Index
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class Friend(Base):
    __tablename__ = "friends"

    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "friend_id"),
        Index("idx_friends_user_id", "user_id"),
        Index("idx_friends_friend_id", "friend_id"),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="friends")

    def __repr__(self):
        return f"<Friend(user={self.user_id}, friend={self.friend_id})>"
