from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, habits, friends, activity, challenges, notifications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])

# Stubs for next stages
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
