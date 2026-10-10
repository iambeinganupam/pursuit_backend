from datetime import datetime, timezone
from typing import Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.api.dependencies import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.db.models.user import User
from app.db.models.auth import RefreshToken
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, RefreshTokenRequest
import jwt

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Check if user exists
    result = await db.execute(
        select(User).filter(
            or_(User.email == user_in.email, User.username == user_in.username)
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this username or email already exists in the system.",
        )
    
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        display_name=user_in.display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    # Authenticate user
    result = await db.execute(
        select(User).filter(User.username == form_data.username)
    )
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(user.id)
    refresh_token_str = create_refresh_token(user.id)
    
    # Decode token to get expiration for DB
    payload = jwt.decode(refresh_token_str, options={"verify_signature": False})
    
    # Store refresh token
    db_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    )
    db.add(db_token)
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Find token in DB
    result = await db.execute(
        select(RefreshToken).filter(RefreshToken.token == request.refresh_token)
    )
    db_token = result.scalars().first()
    
    if not db_token or db_token.revoked_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
        
    # Rotate token - revoke old one
    db_token.revoked_at = datetime.now(timezone.utc)
    
    # Create new tokens
    access_token = create_access_token(db_token.user_id)
    new_refresh_token_str = create_refresh_token(db_token.user_id)
    payload = jwt.decode(new_refresh_token_str, options={"verify_signature": False})
    
    new_db_token = RefreshToken(
        token=new_refresh_token_str,
        user_id=db_token.user_id,
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    )
    db.add(new_db_token)
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_str,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(RefreshToken).filter(
            RefreshToken.token == request.refresh_token,
            RefreshToken.user_id == current_user.id
        )
    )
    db_token = result.scalars().first()
    if db_token and not db_token.revoked_at:
        db_token.revoked_at = datetime.now(timezone.utc)
        await db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    return current_user
