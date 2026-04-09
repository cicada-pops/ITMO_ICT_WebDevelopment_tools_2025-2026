"""Модель пользователя для авторизации."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class PasswordChange(SQLModel):
    old_password: str
    new_password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
