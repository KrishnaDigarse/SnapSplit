from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, PrimaryKeyConstraint, Index
from app.models.types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id = Column(GUID, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("group_id", "user_id"),
        Index("idx_group_members_group_id", "group_id"),
        Index("idx_group_members_user_id", "user_id"),
    )

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")

    def __repr__(self):
        return f"<GroupMember(group={self.group_id}, user={self.user_id})>"
