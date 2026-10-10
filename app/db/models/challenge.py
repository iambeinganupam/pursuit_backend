import uuid
from datetime import date
from typing import Optional
from sqlalchemy import String, ForeignKey, Text, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # E.g., 'most_completions', 'longest_streak'
    challenge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Store rules like min_target, required_habit_category, etc.
    rules: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    creator = relationship("User", foreign_keys=[creator_id])
    memberships: Mapped[list["ChallengeMembership"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")


class ChallengeMembership(Base):
    __tablename__ = "challenge_memberships"

    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # 'invited', 'active', 'left', 'completed'
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    
    # Cache progress here to avoid heavy queries constantly
    progress: Mapped[dict] = mapped_column(JSONB, default=dict)

    challenge: Mapped["Challenge"] = relationship(back_populates="memberships")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("challenge_id", "user_id", name="uq_challenge_membership"),
    )
