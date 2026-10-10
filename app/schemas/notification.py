from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    body: Optional[str]
    data: dict
    is_read: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class NotificationUpdate(BaseModel):
    is_read: bool
