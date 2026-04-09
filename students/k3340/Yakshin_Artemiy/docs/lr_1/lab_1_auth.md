# Авторизация и JWT (задание на 15 баллов)

## Требования задания

- Авторизация и регистрация
- Генерация JWT-токенов
- **Аутентификация по JWT-токену**
- Хэширование паролей
- Дополнительные API-методы для получения информации о пользователе,
  списка пользователей и смены пароля

> «Пожалуйста, реализуйте п.3 вручную, без использования сторонних
> библиотек (хэширование и создание JWT не в счёт).»

**П.3 — «Аутентификация по JWT-токену»** — реализован вручную: без
использования `OAuth2PasswordBearer`, `fastapi-users`, `fastapi-jwt-auth`
и прочих обёрток. Библиотеки `bcrypt` и `PyJWT` применяются только для
хэширования паролей и кодирования/декодирования токенов — и то, и другое
заданием разрешено.

## Хэширование паролей и генерация JWT — `app/auth/security.py`

```python
"""Хэширование паролей и генерация JWT-токенов.

Заданием разрешено использовать сторонние библиотеки для хэширования
и генерации JWT. Мы используем:
  - bcrypt — хэширование паролей;
  - PyJWT — кодирование/декодирование JWT-токенов.

Сама аутентификация (проверка токена и загрузка пользователя) реализована
вручную в модуле app.auth.dependencies.
"""
from datetime import datetime, timedelta
from typing import Any, Dict

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

def create_access_token(subject: str | int, extra: Dict[str, Any] | None = None) -> str:
    """Генерирует JWT-токен с полем sub и временем жизни из настроек."""
    now = datetime.utcnow()
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
```

## Ручная проверка JWT — `app/auth/dependencies.py`

**Это и есть «реализация вручную» п.3.** Мы сами читаем заголовок
`Authorization`, парсим схему, достаём токен, декодируем его и
подгружаем пользователя из БД.

```python
"""Ручная реализация JWT-аутентификации (без OAuth2PasswordBearer).

Здесь мы вручную:
  1) читаем заголовок Authorization;
  2) проверяем, что схема — Bearer;
  3) извлекаем токен и декодируем его;
  4) достаём пользователя из БД по sub.

Именно это задание требует реализовать без сторонних библиотек.
"""
import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session

from app.auth.security import decode_access_token
from app.connection import get_session
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has no subject",
        )

    user = session.get(User, int(sub))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user
```

### Почему это считается «вручную»

1. Не используется `fastapi.security.OAuth2PasswordBearer` — заголовок
   `Authorization` читается напрямую через `fastapi.Header`.
2. Не используется никаких сторонних middleware / depends-обёрток типа
   `fastapi-users`, `fastapi-jwt-auth`, `authlib`.
3. Все проверки (наличие заголовка, схема Bearer, наличие токена,
   декодирование, `exp`, `sub`, факт существования пользователя, флаг
   активности) написаны в одной функции и видны как есть.
4. Зависимость `get_current_user` вручную навешивается на защищённые
   эндпоинты через `Depends(get_current_user)`.

## Регистрация — `POST /auth/register`

```python
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)) -> User:
    exists = session.exec(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
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
```

## Логин — `POST /auth/login`

```python
@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)) -> Token:
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    token = create_access_token(subject=user.id)
    return Token(access_token=token)
```

## Смена пароля — `POST /users/me/change_password`

```python
@router.post("/me/change_password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    session.add(current_user)
    session.commit()
```

## Пример работы через curl

```bash
# Регистрация
curl -X POST http://127.0.0.1:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

# Логин — получаем токен
curl -X POST http://127.0.0.1:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"secret123"}'
# => {"access_token":"eyJhbGciOiJIUzI1NiIs...","token_type":"bearer"}

# Запрос текущего пользователя
curl http://127.0.0.1:8000/users/me \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Смена пароля
curl -X POST http://127.0.0.1:8000/users/me/change_password \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     -H "Content-Type: application/json" \
     -d '{"old_password":"secret123","new_password":"evenmoresecret"}'
```

## Модель `User` и схемы

```python
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
```

## Навигация

- [← Эндпоинты](lab_1_endpoints.md)
- [В начало отчёта](index.md)
