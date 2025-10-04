"""User endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update current user information."""
    update_data = user_in.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in update_data:
        from app.core.security import get_password_hash

        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Get user by ID."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
