import uuid
from sqlalchemy import ForeignKey, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Notification preferences
    push_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Privacy preferences
    # e.g., 'public', 'friends_only', 'private'
    default_activity_visibility: Mapped[str] = mapped_column(String(20), default="friends_only")
    
    # Theme preferences
    theme: Mapped[str] = mapped_column(String(20), default="system")

    user = relationship("User", foreign_keys=[user_id])
