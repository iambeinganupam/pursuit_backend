import uuid
from datetime import date
from typing import Optional
from sqlalchemy import String, ForeignKey, Text, Date, Boolean, Integer, ARRAY, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.user import User


class Habit(Base):
    __tablename__ = "habits"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Simple target, e.g., minutes, pages
    target_value: Mapped[Optional[int]] = mapped_column(Integer)
    target_unit: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    user: Mapped["User"] = relationship()
    schedule: Mapped["HabitSchedule"] = relationship(back_populates="habit", uselist=False, cascade="all, delete-orphan")
    completions: Mapped[list["HabitCompletion"]] = relationship(back_populates="habit", cascade="all, delete-orphan")


class HabitSchedule(Base):
    __tablename__ = "habit_schedules"

    habit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # 0 = Monday, 6 = Sunday. Empty means everyday if is_daily is true, else none.
    # For a robust approach, we can store list of weekday integers
    weekdays: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    is_daily: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_time: Mapped[Optional[str]] = mapped_column(String(5)) # HH:MM format
    
    # Relationships
    habit: Mapped["Habit"] = relationship(back_populates="schedule")


class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    habit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Date of completion in user's timezone, ensuring unique per habit per date
    completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Optional value recorded, e.g., how many minutes out of target_value
    value_recorded: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    habit: Mapped["Habit"] = relationship(back_populates="completions")

    __table_args__ = (
        UniqueConstraint("habit_id", "completion_date", name="uq_habit_completion_date"),
    )
