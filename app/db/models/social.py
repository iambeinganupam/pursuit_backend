import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, UniqueConstraint, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Friendship(Base):
    __tablename__ = "friendships"

    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    addressee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # status can be 'pending', 'accepted', 'rejected'
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])

    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship"),
    )


class Activity(Base):
    __tablename__ = "activities"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # e.g., 'habit_completed', 'streak_achieved', 'challenge_joined', 'challenge_completed'
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # JSON data for rendering, e.g., {"habit_id": "...", "habit_title": "...", "streak": 5}
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict)

    # visibility settings - can be public, friends_only, private
    visibility: Mapped[str] = mapped_column(String(20), default="friends_only", nullable=False)

    user = relationship("User", foreign_keys=[user_id])
