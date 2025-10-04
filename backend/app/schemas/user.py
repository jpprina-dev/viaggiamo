"""User schemas for API serialization."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: str
    phone: str | None = None
    profile_picture: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    password: str | None = None


class UserInDB(UserBase):
    """Schema for user in database."""

    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class User(UserInDB):
    """Schema for user response."""

    pass


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: int | None = None
