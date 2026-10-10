from pydantic import BaseModel, Field
import uuid
from typing import Optional, List
from datetime import datetime, date
from app.schemas.user import UserResponse


class ChallengeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: date
    end_date: date
    challenge_type: str = Field(..., max_length=50)
    rules: dict = Field(default_factory=dict)


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    end_date: Optional[date] = None
    rules: Optional[dict] = None


class ChallengeMembershipResponse(BaseModel):
    id: uuid.UUID
    challenge_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    progress: dict
    created_at: datetime
    updated_at: datetime
    
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class ChallengeResponse(ChallengeBase):
    id: uuid.UUID
    creator_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    creator: Optional[UserResponse] = None
    memberships: List[ChallengeMembershipResponse] = []

    model_config = {"from_attributes": True}
