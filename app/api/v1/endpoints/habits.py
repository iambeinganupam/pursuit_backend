from typing import Any, List
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.habit import Habit, HabitSchedule, HabitCompletion
from app.schemas.habit import (
    HabitCreate, HabitUpdate, HabitResponse, 
    HabitCompletionCreate, HabitCompletionResponse
)

router = APIRouter()


@router.get("", response_model=List[HabitResponse])
async def get_habits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit)
        .options(selectinload(Habit.schedule))
        .filter(Habit.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=HabitResponse)
async def create_habit(
    habit_in: HabitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    habit_data = habit_in.model_dump(exclude={"schedule"})
    schedule_data = habit_in.schedule.model_dump()
    
    habit = Habit(**habit_data, user_id=current_user.id)
    db.add(habit)
    await db.flush() # get habit id
    
    schedule = HabitSchedule(**schedule_data, habit_id=habit.id)
    db.add(schedule)
    await db.commit()
    
    # Reload with schedule
    result = await db.execute(
        select(Habit)
        .options(selectinload(Habit.schedule))
        .filter(Habit.id == habit.id)
    )
    return result.scalars().first()


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit)
        .options(selectinload(Habit.schedule))
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: uuid.UUID,
    habit_in: HabitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit)
        .options(selectinload(Habit.schedule))
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    update_data = habit_in.model_dump(exclude_unset=True)
    if "schedule" in update_data:
        schedule_data = update_data.pop("schedule")
        for field, value in schedule_data.items():
            setattr(habit.schedule, field, value)
            
    for field, value in update_data.items():
        setattr(habit, field, value)
        
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    await db.delete(habit)
    await db.commit()
    return {"message": "Habit deleted"}


# Completions sub-routes

@router.post("/{habit_id}/completions", response_model=HabitCompletionResponse)
async def complete_habit(
    habit_id: uuid.UUID,
    completion_in: HabitCompletionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Check ownership
    result = await db.execute(
        select(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    completion = HabitCompletion(
        habit_id=habit.id,
        completion_date=completion_in.completion_date,
        value_recorded=completion_in.value_recorded
    )
    db.add(completion)
    try:
        await db.commit()
        await db.refresh(completion)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Habit already completed for this date")
        
    return completion


@router.delete("/{habit_id}/completions/{completion_date}")
async def delete_completion(
    habit_id: uuid.UUID,
    completion_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Habit not found")
        
    result = await db.execute(
        select(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date == completion_date
        )
    )
    completion = result.scalars().first()
    if not completion:
        raise HTTPException(status_code=404, detail="Completion not found")
        
    await db.delete(completion)
    await db.commit()
    return {"message": "Completion deleted"}


@router.get("/{habit_id}/completions", response_model=List[HabitCompletionResponse])
async def get_completions(
    habit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Habit not found")
        
    result = await db.execute(
        select(HabitCompletion).filter(HabitCompletion.habit_id == habit_id).order_by(HabitCompletion.completion_date.desc())
    )
    return result.scalars().all()
