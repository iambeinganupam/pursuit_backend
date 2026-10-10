import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # E.g., 'friend_request', 'friend_accepted', 'challenge_invite', 'habit_reminder'
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(String(1024))
    
    # JSON data for navigation/actions
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("User", foreign_keys=[user_id])
