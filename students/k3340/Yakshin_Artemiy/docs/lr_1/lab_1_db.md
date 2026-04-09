---
title: Подключение к БД
---

# Подключение к БД и миграции

## Код подключения — `app/connection.py`

```python
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
```

- `engine` создаётся на базе `settings.DB_ADMIN`, значение которого
  читается из переменной окружения `DB_ADMIN` в `.env` через
  `python-dotenv`.
- `echo=True` — все SQL-запросы логируются, удобно для отладки.
- `init_db()` — создаёт все таблицы, определённые в моделях. Важно сначала
  импортировать `app.models` — при импорте пакета отрабатывает его
  `__init__.py`, где перечислены все таблицы, и они регистрируются
  в `SQLModel.metadata`.
- `get_session()` — генератор, используется с `Depends(get_session)` во
  всех роутерах.

## Конфигурация — `app/config.py`

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

## Файл `.env.example`

Реальный `.env` не коммитится (добавлен в `.gitignore`).
`.env.example` показывает, какие переменные нужны:

```env
DB_ADMIN=postgresql://postgres:123@localhost/hackathons_db
JWT_SECRET=please-change-me-to-a-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```

## Инициализация на старте — `main.py`

```python
@app.on_event("startup")
def on_startup() -> None:
    init_db()
```

## Миграции Alembic

### `alembic.ini`

`sqlalchemy.url` оставлен пустым — он подставляется программно из `.env`
в `migrations/env.py`.

```ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url =
```

### `migrations/env.py`

```python
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Добавляем корень проекта в sys.path, чтобы работали импорты из app.*
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Импорт всех моделей — необходимо, чтобы Alembic видел metadata
import app.models  # noqa: F401

config = context.config

# URL БД подгружаем из .env и подставляем в alembic-конфиг программно
load_dotenv()
db_url = os.getenv("DB_ADMIN")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Начальная миграция

`migrations/versions/0001_initial.py` — создаёт все таблицы, описанные
выше (`location`, `participant`, `user`, `hackathon`, `team`, `task`,
`teamparticipantlink`, `submission`), включая enum-типы `hackathonstatus`
и `teamrole`, индексы по `user.username` и `user.email`.

### Команды

```bash
# Применить все миграции
alembic upgrade head

# Сгенерировать новую миграцию по изменениям в моделях
alembic revision --autogenerate -m "описание"

# Откатить последнюю миграцию
alembic downgrade -1

# Посмотреть текущую ревизию
alembic current
```

## Навигация

- [← Модели данных](lab_1_models.md)
- [Эндпоинты →](lab_1_endpoints.md)
