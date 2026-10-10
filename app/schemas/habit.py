from pydantic import BaseModel, Field
import uuid
from typing import Optional, List
from datetime import datetime, date


class HabitScheduleBase(BaseModel):
    weekdays: List[int] = Field(default_factory=list)
    is_daily: bool = True
    reminder_time: Optional[str] = None # HH:MM


class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    target_value: Optional[int] = None
    target_unit: Optional[str] = Field(None, max_length=50)


class HabitCreate(HabitBase):
    schedule: HabitScheduleBase


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    is_archived: Optional[bool] = None
    target_value: Optional[int] = None
    target_unit: Optional[str] = None
    schedule: Optional[HabitScheduleBase] = None


class HabitScheduleResponse(HabitScheduleBase):
    id: uuid.UUID
    
    model_config = {"from_attributes": True}


class HabitResponse(HabitBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    is_completed_today: bool = False
    schedule: HabitScheduleResponse

    model_config = {"from_attributes": True}


class HabitCompletionCreate(BaseModel):
    completion_date: date
    value_recorded: Optional[int] = None


class HabitCompletionResponse(BaseModel):
    id: uuid.UUID
    habit_id: uuid.UUID
    completion_date: date
    value_recorded: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
