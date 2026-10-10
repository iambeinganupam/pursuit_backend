from pydantic import BaseModel
import uuid
from typing import Optional


class UserSettingsBase(BaseModel):
    push_notifications_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    default_activity_visibility: Optional[str] = None
    theme: Optional[str] = None


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    push_notifications_enabled: bool
    email_notifications_enabled: bool
    default_activity_visibility: str
    theme: str
    
    model_config = {"from_attributes": True}
