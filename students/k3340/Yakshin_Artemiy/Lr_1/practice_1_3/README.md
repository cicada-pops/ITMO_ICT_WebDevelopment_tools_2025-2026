# Practice 1.3 — Alembic + .env

Доработка practice_1_2: система миграций Alembic и вынос URL БД в `.env`.

## Что добавлено

- `alembic.ini` — конфиг Alembic. Ключ `sqlalchemy.url` оставлен пустым
  и **переопределяется программно в `migrations/env.py`** из `.env`.
- `migrations/env.py` — подгружает `DB_ADMIN` из `.env`, импортирует модели,
  указывает `target_metadata = SQLModel.metadata`.
- `migrations/script.py.mako` — шаблон с импортом `sqlmodel`.
- Миграции в `migrations/versions/`:
  - `0001_initial.py` — создание всех таблиц.
  - `0002_add_joined_at.py` — добавление поля `joined_at` в ассоциативную
    таблицу `teamparticipantlink` (демонстрация того, как добавлять поле
    в уже существующую таблицу через миграцию).
- `.env.example` — шаблон переменных окружения.
- `.gitignore` — исключает `*.env`, `__pycache__`, IDE-файлы и т.п.
- `connection.py` — подключение БД через `os.getenv("DB_ADMIN")`
  и `python-dotenv`.

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env     # отредактировать DB_ADMIN под себя
alembic upgrade head     # применить все миграции
uvicorn main:app --reload
```

## Создание новой миграции (автогенерация)

```bash
alembic revision --autogenerate -m "описание изменения"
alembic upgrade head
```

## Как URL БД передаётся в alembic.ini через .env

В `alembic.ini` ключ `sqlalchemy.url` оставлен пустым. В `migrations/env.py`
вызывается `load_dotenv()`, читается `os.getenv("DB_ADMIN")` и значение
подставляется через `config.set_main_option("sqlalchemy.url", db_url)`.
Это позволяет не хранить креды БД в версионируемом `alembic.ini`.
