from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class FriendshipRequest(BaseModel):
    addressee_id: uuid.UUID


class FriendshipResponse(BaseModel):
    id: uuid.UUID
    requester_id: uuid.UUID
    addressee_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Optional nested user details for the other party
    requester: Optional[UserResponse] = None
    addressee: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class ActivityResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    metadata_: dict
    visibility: str
    created_at: datetime
    
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}
