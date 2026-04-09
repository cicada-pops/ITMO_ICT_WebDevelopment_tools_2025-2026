"""Настройки приложения, читаются из переменных окружения (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_ADMIN: str = os.getenv(
        "DB_ADMIN", "postgresql://postgres:123@localhost/hackathons_db"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))


settings = Settings()
