import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, Enum as SQLEnum
from app.models.types import GUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class FriendRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    sender_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(FriendRequestStatus), default=FriendRequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")

    def __repr__(self):
        return f"<FriendRequest(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id}, status={self.status})>"
