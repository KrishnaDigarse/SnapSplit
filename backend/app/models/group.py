import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Enum as SQLEnum
from app.models.types import GUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class GroupType(str, enum.Enum):
    GROUP = "GROUP"
    DIRECT = "DIRECT"


class Group(Base):
    __tablename__ = "groups"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(SQLEnum(GroupType), default=GroupType.GROUP, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="groups_created")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="group", cascade="all, delete-orphan")
    balances = relationship("GroupBalance", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, type={self.type})>"
