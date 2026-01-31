import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.types import GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sent_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
    friends = relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    groups_created = relationship(
        "Group",
        foreign_keys="Group.created_by",
        back_populates="creator"
    )
    group_memberships = relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    expenses_created = relationship(
        "Expense",
        back_populates="creator"
    )
    splits = relationship(
        "Split",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    settlements_paid = relationship(
        "Settlement",
        foreign_keys="Settlement.paid_by",
        back_populates="payer"
    )
    settlements_received = relationship(
        "Settlement",
        foreign_keys="Settlement.paid_to",
        back_populates="payee"
    )
    group_balances = relationship(
        "GroupBalance",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
