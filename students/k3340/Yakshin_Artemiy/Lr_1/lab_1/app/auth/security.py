"""Хэширование паролей и генерация JWT-токенов.

Заданием разрешено использовать сторонние библиотеки для хэширования
и генерации JWT. Мы используем:
  - bcrypt — хэширование паролей;
  - PyJWT — кодирование/декодирование JWT-токенов.

Сама аутентификация (проверка токена и загрузка пользователя) реализована
вручную в модуле app.auth.dependencies.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import bcrypt
import jwt

from app.config import settings


# ---------- Пароли ----------

def hash_password(password: str) -> str:
    """Хэширует пароль с помощью bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против bcrypt-хэша."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


# ---------- JWT ----------

def create_access_token(
    subject: Union[str, int], extra: Optional[Dict[str, Any]] = None
) -> str:
    """Генерирует JWT-токен с полем sub и временем жизни из настроек."""
    # Важно: timezone-aware UTC, иначе naive datetime даст смещение при timestamp().
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Декодирует и валидирует JWT. Бросает jwt.PyJWTError при ошибке."""
    return jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
