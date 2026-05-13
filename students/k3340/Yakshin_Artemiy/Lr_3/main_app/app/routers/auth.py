"""Роутер регистрации и логина."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.security import create_access_token, hash_password, verify_password
from app.connection import get_session
from app.models.user import Token, User, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate, session: Session = Depends(get_session)
) -> User:
    exists = session.exec(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )
    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)) -> Token:
    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)
