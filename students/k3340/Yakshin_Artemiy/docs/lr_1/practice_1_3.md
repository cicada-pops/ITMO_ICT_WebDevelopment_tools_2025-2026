---
title: Практика 1.3 — Alembic + .env
---

# Практика 1.3 — Alembic + `.env`

## Задание

1. Реализовать в проекте все улучшения, описанные в практике.
2. Разобраться, как передать в `alembic.ini` URL базы данных через `.env`,
   и реализовать такую передачу.

## Результат

- Установлен `alembic`, инициализирована папка `migrations/`.
- `alembic.ini` настроен так, что `sqlalchemy.url` подставляется программно
  из `.env`, а не хранится в коде.
- Создана начальная миграция `0001_initial` (все таблицы).
- Создана вторая миграция `0002_add_joined_at`, добавляющая поле `joined_at`
  в ассоциативную таблицу `teamparticipantlink` — демонстрация изменения
  существующей схемы через миграцию.
- Добавлены `.env`, `.env.example`, `.gitignore`.

## `.env` и `.gitignore`

`.env.example`:

```env
DB_ADMIN=postgresql://postgres:123@localhost/hackathons_db
```

`.gitignore`:

```gitignore
*.env
!.env.example
__pycache__/
.venv/
.idea/
.DS_Store
```

## Подключение БД через переменные окружения

`practice_1_3/connection.py`:

```python
import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

db_url = os.getenv("DB_ADMIN", "postgresql://postgres:123@localhost/hackathons_db")
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

## Настройка Alembic

### `alembic.ini`

Важно: **значение `sqlalchemy.url` оставлено пустым**, потому что URL БД
подставляется программно в `migrations/env.py`.

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

# Добавляем корень проекта в sys.path, чтобы работали импорты models
sys.path.append(str(Path(__file__).resolve().parents[1]))
from models import *  # noqa: F401,F403

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
```

### `script.py.mako`

В шаблон добавлен импорт `sqlmodel`, чтобы автогенерированные миграции
использовали `sqlmodel.sql.sqltypes.AutoString`:

```python
import sqlmodel
```

## Миграция добавления поля в ассоциативную таблицу

`migrations/versions/0002_add_joined_at.py`:

```python
"""add joined_at field to teamparticipantlink

Revision ID: 0002_add_joined_at
Revises: 0001_initial
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_add_joined_at"
down_revision = "0001_initial"


def upgrade() -> None:
    op.add_column(
        "teamparticipantlink",
        sa.Column("joined_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("teamparticipantlink", "joined_at")
```

## Команды

```bash
# Создать новую миграцию автогенерацией
alembic revision --autogenerate -m "описание изменения"

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Посмотреть текущую ревизию
alembic current
```

## Ссылки

- Исходный код — [`Lr_1/practice_1_3/`](../../Lr_1/practice_1_3/)
- [← Практика 1.2](practice_1_2.md) | [Далее: Лабораторная работа →](lab_1.md)
