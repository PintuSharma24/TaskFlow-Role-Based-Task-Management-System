
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str = Field(min_length=1)
    role: Literal["admin", "manager", "employee"]


class UserResponse(BaseModel):
    """Public user information returned after login."""

    id: int
    name: str
    email: EmailStr
    role: str


class LoginResponse(BaseModel):
    """Schema for successful login response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
