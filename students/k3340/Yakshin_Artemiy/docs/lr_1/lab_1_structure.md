# Структура проекта `lab_1/`

```
lab_1/
├── main.py                  # точка входа (создаёт FastAPI, подключает роутеры)
├── alembic.ini              # конфиг Alembic (url подставляется из .env)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── migrations/              # миграции Alembic
│   ├── env.py
│   ├── script.py.mako
│   ├── README
│   └── versions/
│       └── 0001_initial.py
└── app/
    ├── __init__.py
    ├── config.py            # настройки (DB_ADMIN, JWT_SECRET и пр.)
    ├── connection.py        # engine, init_db, get_session
    ├── auth/                # авторизация
    │   ├── __init__.py
    │   ├── security.py      # hash_password / verify_password / JWT
    │   └── dependencies.py  # ручная проверка JWT (без OAuth2PasswordBearer)
    ├── models/              # SQLModel-модели по доменам
    │   ├── __init__.py      # агрегатор, rebuild forward refs
    │   ├── enums.py
    │   ├── associations.py  # TeamParticipantLink, Submission
    │   ├── location.py
    │   ├── hackathon.py
    │   ├── team.py
    │   ├── participant.py
    │   ├── task.py
    │   └── user.py
    └── routers/             # эндпоинты по доменам
        ├── __init__.py
        ├── auth.py
        ├── users.py
        ├── locations.py
        ├── hackathons.py
        ├── teams.py
        ├── participants.py
        └── tasks.py
```

## Принципы разделения

- **`app/models/`** — всё, что касается схемы данных. Каждая сущность
  в отдельном файле; ассоциативные сущности вынесены в `associations.py`,
  enums — в `enums.py`. Агрегатор `__init__.py` импортирует все модели
  (нужно, чтобы они попали в `SQLModel.metadata` для Alembic и
  `init_db`), а также вызывает `model_rebuild()` для read-моделей с
  forward references.
- **`app/routers/`** — эндпоинты FastAPI, по одному роутеру на предметную
  область. Подключаются в `main.py` через `app.include_router(...)`.
- **`app/auth/`** — изолированная подсистема безопасности.
  `security.py` — утилиты хэширования паролей и работы с JWT.
  `dependencies.py` — ручная зависимость `get_current_user`.
- **`app/config.py`** — чтение переменных окружения.
- **`app/connection.py`** — создание движка, инициализация БД, генератор
  сессий.
- **`migrations/`** — Alembic. URL БД **не хранится в `alembic.ini`**,
  а подставляется программно в `env.py` из переменной окружения `DB_ADMIN`.
- **`main.py`** — тонкая точка входа: создаёт `FastAPI`, вешает хук
  `on_startup`, подключает роутеры.

## `main.py`

```python
"""Точка входа приложения Hackathons API."""
from fastapi import FastAPI

from app.connection import init_db
from app.routers import (
    auth, hackathons, locations, participants, tasks, teams, users,
)

app = FastAPI(
    title="Hackathons API",
    description="Система для проведения хакатонов — лабораторная работа №1.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(hackathons.router)
app.include_router(participants.router)
app.include_router(teams.router)
app.include_router(tasks.router)
```

## Настройки

`app/config.py`:

```python
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
```

## Навигация

- [← Обзор лабораторной работы](lab_1.md)
- [Модели данных →](lab_1_models.md)
