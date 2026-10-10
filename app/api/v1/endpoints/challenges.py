from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.challenge import Challenge, ChallengeMembership
from app.db.models.social import Activity
from app.schemas.challenge import ChallengeCreate, ChallengeResponse

router = APIRouter()


@router.get("", response_model=List[ChallengeResponse])
async def get_challenges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Get challenges where user is a member or creator
    result = await db.execute(
        select(Challenge)
        .join(ChallengeMembership, Challenge.id == ChallengeMembership.challenge_id, isouter=True)
        .options(selectinload(Challenge.creator), selectinload(Challenge.memberships).selectinload(ChallengeMembership.user))
        .filter(
            (Challenge.creator_id == current_user.id) | 
            (ChallengeMembership.user_id == current_user.id)
        )
    )
    # Deduplicate results due to outer join
    challenges = result.unique().scalars().all()
    return challenges


@router.post("", response_model=ChallengeResponse)
async def create_challenge(
    challenge_in: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    challenge = Challenge(
        title=challenge_in.title,
        description=challenge_in.description,
        start_date=challenge_in.start_date,
        end_date=challenge_in.end_date,
        challenge_type=challenge_in.challenge_type,
        rules=challenge_in.rules,
        creator_id=current_user.id
    )
    db.add(challenge)
    await db.flush()
    
    # Add creator as a member
    membership = ChallengeMembership(
        challenge_id=challenge.id,
        user_id=current_user.id,
        status="active"
    )
    db.add(membership)
    await db.commit()
    
    # Reload with relations
    result = await db.execute(
        select(Challenge)
        .options(selectinload(Challenge.creator), selectinload(Challenge.memberships).selectinload(ChallengeMembership.user))
        .filter(Challenge.id == challenge.id)
    )
    return result.scalars().first()


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Challenge)
        .options(selectinload(Challenge.creator), selectinload(Challenge.memberships).selectinload(ChallengeMembership.user))
        .filter(Challenge.id == challenge_id)
    )
    challenge = result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    return challenge


@router.post("/{challenge_id}/join", response_model=ChallengeResponse)
async def join_challenge(
    challenge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Challenge).filter(Challenge.id == challenge_id)
    )
    challenge = result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    membership = ChallengeMembership(
        challenge_id=challenge.id,
        user_id=current_user.id,
        status="active"
    )
    db.add(membership)
    
    # Optionally record activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="challenge_joined",
        metadata_={"challenge_id": str(challenge.id), "challenge_title": challenge.title},
        visibility="friends_only"
    )
    db.add(activity)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already a member of this challenge")
        
    result = await db.execute(
        select(Challenge)
        .options(selectinload(Challenge.creator), selectinload(Challenge.memberships).selectinload(ChallengeMembership.user))
        .filter(Challenge.id == challenge_id)
    )
    return result.scalars().first()


@router.post("/{challenge_id}/leave")
async def leave_challenge(
    challenge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(ChallengeMembership).filter(
            ChallengeMembership.challenge_id == challenge_id,
            ChallengeMembership.user_id == current_user.id
        )
    )
    membership = result.scalars().first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
        
    await db.delete(membership)
    await db.commit()
    return {"message": "Left challenge successfully"}


@router.get("/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(
    challenge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(ChallengeMembership)
        .options(selectinload(ChallengeMembership.user))
        .filter(ChallengeMembership.challenge_id == challenge_id)
    )
    memberships = result.scalars().all()
    
    # In a real app, you would compute progress here or use a cached progress field
    # For MVP, we will return the memberships containing the cached progress.
    # Typically, the frontend reads the `progress` json to construct the leaderboard.
    return memberships
