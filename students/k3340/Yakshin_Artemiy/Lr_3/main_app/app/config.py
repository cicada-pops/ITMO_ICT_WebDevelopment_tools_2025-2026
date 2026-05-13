"""Настройки приложения, читаются из переменных окружения (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_ADMIN: str = os.getenv(
        "DB_ADMIN", "postgresql://postgres:postgres@db:5432/hackathons_db"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    PARSER_URL: str = os.getenv("PARSER_URL", "http://parser:8001")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/1"
    )


settings = Settings()
