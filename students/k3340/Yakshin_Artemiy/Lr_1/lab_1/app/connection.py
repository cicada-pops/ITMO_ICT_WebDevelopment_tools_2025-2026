"""Подключение к БД и фабрика сессий."""
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.DB_ADMIN, echo=True)


def init_db() -> None:
    # Импорт ради регистрации всех моделей в SQLModel.metadata
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
