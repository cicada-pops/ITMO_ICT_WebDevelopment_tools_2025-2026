# Лабораторная работа №1 — Hackathons API

Серверное приложение на **FastAPI + SQLModel + PostgreSQL** для проведения
хакатонов. Собрано на основе практик 1.1–1.3 с добавлением подсистемы
авторизации (JWT).

## Структура проекта

```
lab_1/
├── main.py                  # точка входа (создаёт FastAPI, подключает роутеры)
├── alembic.ini              # конфиг alembic (url подставляется из .env)
├── requirements.txt
├── .env.example
├── .gitignore
├── migrations/              # миграции Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial.py
└── app/
    ├── config.py            # настройки (DB_ADMIN, JWT_SECRET и пр.)
    ├── connection.py        # engine, init_db, get_session
    ├── auth/                # авторизация
    │   ├── security.py      # hash_password / verify_password / JWT
    │   └── dependencies.py  # ручная проверка JWT (без OAuth2PasswordBearer)
    ├── models/              # SQLModel-модели по доменам
    │   ├── enums.py
    │   ├── associations.py  # TeamParticipantLink, Submission
    │   ├── location.py
    │   ├── hackathon.py
    │   ├── team.py
    │   ├── participant.py
    │   ├── task.py
    │   └── user.py
    └── routers/             # эндпоинты по доменам
        ├── auth.py
        ├── users.py
        ├── locations.py
        ├── hackathons.py
        ├── teams.py
        ├── participants.py
        └── tasks.py
```

## Модель данных (7 таблиц)

- **`Location`** — площадка хакатона.
- **`Hackathon`** — хакатон (статус, описание, FK `location_id`).
- **`Team`** — команда (FK `hackathon_id`).
- **`Participant`** — участник.
- **`Task`** — задача (FK `hackathon_id`).
- **`TeamParticipantLink`** — ассоциативная сущность `Team ↔ Participant`
  с полями `role` и `joined_at`.
- **`Submission`** — ассоциативная сущность `Team ↔ Task` с полями
  `repo_url`, `score`, `submitted_at`.
- **`User`** — пользователь с логином, хэшированным паролем, флагом `is_active`.

### Связи

| Тип | Сущности |
|-----|----------|
| o2m | `Location` → `Hackathon` |
| o2m | `Hackathon` → `Team` |
| o2m | `Hackathon` → `Task` |
| m2m | `Team` ↔ `Participant` через `TeamParticipantLink` (поле `role`) |
| m2m | `Team` ↔ `Task` через `Submission` (поля `repo_url`, `score`) |

Ассоциативные сущности содержат **поля, характеризующие связь**, что
удовлетворяет критерию ЛР.

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                    # отредактировать под себя
alembic upgrade head                    # накатить миграции
uvicorn main:app --reload
```

Swagger: <http://127.0.0.1:8000/docs>

## Эндпоинты

### Auth

| Метод | Путь | Описание |
|-------|------|----------|
| POST  | `/auth/register` | Регистрация пользователя |
| POST  | `/auth/login`    | Логин, выдача JWT |

### Users (требуют `Authorization: Bearer <token>`)

| Метод | Путь | Описание |
|-------|------|----------|
| GET   | `/users/me` | Текущий пользователь |
| GET   | `/users` | Список пользователей |
| GET   | `/users/{user_id}` | Пользователь по id |
| POST  | `/users/me/change_password` | Смена пароля |

### Предметная область (CRUD)

Для каждой сущности: `GET /{entity}`, `GET /{entity}/{id}`, `POST /{entity}`,
`PATCH /{entity}/{id}`, `DELETE /{entity}/{id}`.

- `/locations`
- `/hackathons` — `GET /hackathons/{id}` возвращает вложенные `location`,
  `teams`, `tasks` (o2m).
- `/participants` — `GET /participants/{id}` возвращает вложенные команды.
- `/teams` — `GET /teams/{id}` возвращает вложенных `participants` и
  `tasks` (обе m2m).
- `/tasks` — `GET /tasks/{id}` возвращает вложенные команды (m2m).

### Управление связями m2m

| Метод | Путь | Описание |
|-------|------|----------|
| POST  | `/teams/{team_id}/members/{participant_id}?role=developer` | Добавить участника в команду |
| POST  | `/teams/{team_id}/submissions/{task_id}?repo_url=...&score=...` | Сдать решение по задаче |

## Авторизация

В соответствии с требованием задания («Аутентификацию по JWT-токену
реализовать вручную, без использования сторонних библиотек»):

- **Хэширование паролей** — `bcrypt` (разрешено заданием).
- **Генерация JWT** — `PyJWT` (разрешено заданием).
- **Проверка JWT и загрузка пользователя** — написана вручную в
  `app/auth/dependencies.py::get_current_user`:
  - читает заголовок `Authorization` через `fastapi.Header`;
  - валидирует схему `Bearer`;
  - декодирует токен, отдельно обрабатывает истёкший / невалидный;
  - по `sub` достаёт пользователя из БД;
  - **не используется** `OAuth2PasswordBearer`, `fastapi-users`,
    `fastapi-jwt-auth` и прочие сторонние обёртки над авторизацией.

Пример запроса к защищённому эндпоинту:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"secret"}'
# => {"access_token":"eyJhbGciOi...","token_type":"bearer"}

curl http://127.0.0.1:8000/users/me \
     -H "Authorization: Bearer eyJhbGciOi..."
```

## Миграции

```bash
alembic revision --autogenerate -m "описание"
alembic upgrade head
alembic downgrade -1
```

URL БД в `alembic.ini` оставлен пустым и подставляется в `migrations/env.py`
из переменной окружения `DB_ADMIN`, загружаемой `python-dotenv`.
