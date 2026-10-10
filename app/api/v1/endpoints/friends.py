from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.social import Friendship, Activity
from app.schemas.social import FriendshipRequest, FriendshipResponse

router = APIRouter()


@router.get("", response_model=List[FriendshipResponse])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Get all accepted friendships where current_user is either requester or addressee
    result = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester), selectinload(Friendship.addressee))
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.addressee_id == current_user.id
            ),
            Friendship.status == "accepted"
        )
    )
    return result.scalars().all()


@router.get("/requests", response_model=List[FriendshipResponse])
async def get_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Incoming and outgoing pending requests
    result = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester), selectinload(Friendship.addressee))
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.addressee_id == current_user.id
            ),
            Friendship.status == "pending"
        )
    )
    return result.scalars().all()


@router.post("/requests", response_model=FriendshipResponse)
async def send_friend_request(
    request: FriendshipRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if current_user.id == request.addressee_id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
        
    # Check if target user exists
    target = await db.execute(select(User).filter(User.id == request.addressee_id))
    if not target.scalars().first():
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if a relationship already exists (either direction)
    existing = await db.execute(
        select(Friendship).filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == request.addressee_id),
                and_(Friendship.requester_id == request.addressee_id, Friendship.addressee_id == current_user.id)
            )
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Friendship or request already exists")
        
    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=request.addressee_id,
        status="pending"
    )
    db.add(friendship)
    await db.commit()
    
    # Reload with relations
    result = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester), selectinload(Friendship.addressee))
        .filter(Friendship.id == friendship.id)
    )
    return result.scalars().first()


@router.post("/requests/{request_id}/accept", response_model=FriendshipResponse)
async def accept_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester), selectinload(Friendship.addressee))
        .filter(Friendship.id == request_id, Friendship.addressee_id == current_user.id)
    )
    friendship = result.scalars().first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if friendship.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending")
        
    friendship.status = "accepted"
    db.add(friendship)
    
    # Optionally, generate activity here or in a separate task
    activity = Activity(
        user_id=current_user.id,
        activity_type="friend_accepted",
        metadata_={"friend_id": str(friendship.requester_id), "friend_name": friendship.requester.username},
        visibility="friends_only"
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(friendship)
    return friendship


@router.post("/requests/{request_id}/reject")
async def reject_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Friendship).filter(
            Friendship.id == request_id,
            or_(
                Friendship.addressee_id == current_user.id,
                Friendship.requester_id == current_user.id # Allow canceling outgoing request
            )
        )
    )
    friendship = result.scalars().first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
        
    await db.delete(friendship)
    await db.commit()
    return {"message": "Friend request removed"}


@router.delete("/{user_id}")
async def remove_friend(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Friendship).filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == user_id),
                and_(Friendship.requester_id == user_id, Friendship.addressee_id == current_user.id)
            ),
            Friendship.status == "accepted"
        )
    )
    friendship = result.scalars().first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
        
    await db.delete(friendship)
    await db.commit()
    return {"message": "Friend removed"}
