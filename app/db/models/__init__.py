from app.db.base import Base

from app.db.models.user import User
from app.db.models.auth import RefreshToken
from app.db.models.habit import Habit, HabitSchedule, HabitCompletion
from app.db.models.social import Friendship, Activity
from app.db.models.challenge import Challenge, ChallengeMembership
from app.db.models.notification import Notification
from app.db.models.settings import UserSettings

# For Alembic to discover all models, they just need to be imported here
__all__ = [
    "Base",
    "User",
    "RefreshToken",
    "Habit",
    "HabitSchedule",
    "HabitCompletion",
    "Friendship",
    "Activity",
    "Challenge",
    "ChallengeMembership",
    "Notification",
    "UserSettings",
]
