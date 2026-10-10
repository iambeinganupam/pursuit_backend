from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.social import Friendship, Activity
from app.schemas.social import ActivityResponse

router = APIRouter()


@router.get("/feed", response_model=List[ActivityResponse])
async def get_activity_feed(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Get list of friend IDs
    friends_req = await db.execute(
        select(Friendship)
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.addressee_id == current_user.id
            ),
            Friendship.status == "accepted"
        )
    )
    friendships = friends_req.scalars().all()
    friend_ids = []
    for f in friendships:
        if f.requester_id == current_user.id:
            friend_ids.append(f.addressee_id)
        else:
            friend_ids.append(f.requester_id)
            
    # Include own activities as well (public or friends_only)
    target_users = friend_ids + [current_user.id]
    
    # Simple query for MVP: get activities from target users 
    # where visibility is public or friends_only (or private if it's the current user)
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.user))
        .filter(
            Activity.user_id.in_(target_users),
            or_(
                Activity.user_id == current_user.id,
                Activity.visibility.in_(["public", "friends_only"])
            )
        )
        .order_by(Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()
