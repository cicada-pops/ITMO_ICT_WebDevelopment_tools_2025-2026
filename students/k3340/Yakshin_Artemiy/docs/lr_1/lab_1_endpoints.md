# Эндпоинты

Эндпоинты разнесены по файлам в `app/routers/`, каждый — с префиксом и
тегом для Swagger. Везде используется аннотация типов как во входных
параметрах, так и в возвращаемых значениях (`response_model`).

## Сводная таблица

### Auth (публичные)

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| POST  | `/auth/register` | `UserRead` | Регистрация пользователя |
| POST  | `/auth/login`    | `Token` | Логин, выдача JWT |

### Users (JWT)

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/users/me` | `UserRead` | Текущий пользователь |
| GET   | `/users` | `List[UserRead]` | Список пользователей |
| GET   | `/users/{user_id}` | `UserRead` | Пользователь по id |
| POST  | `/users/me/change_password` | 204 | Смена пароля |

### Locations

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/locations` | `List[LocationRead]` | Список локаций |
| GET   | `/locations/{id}` | `LocationRead` | Локация по id |
| POST  | `/locations` | `LocationRead` | Создать (JWT) |
| PATCH | `/locations/{id}` | `LocationRead` | Обновить (JWT) |
| DELETE| `/locations/{id}` | `{"ok": true}` | Удалить (JWT) |

### Hackathons

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/hackathons` | `List[HackathonRead]` | Список хакатонов |
| GET   | `/hackathons/{id}` | **`HackathonReadFull`** | Хакатон **с вложенными** `location`, `teams`, `tasks` (o2m) |
| POST  | `/hackathons` | `HackathonRead` | Создать (JWT) |
| PATCH | `/hackathons/{id}` | `HackathonRead` | Обновить (JWT) |
| DELETE| `/hackathons/{id}` | `{"ok": true}` | Удалить (JWT) |

### Participants

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/participants` | `List[ParticipantRead]` | Список участников |
| GET   | `/participants/{id}` | **`ParticipantReadWithTeams`** | Участник с вложенными командами (m2m) |
| POST  | `/participants` | `ParticipantRead` | Создать (JWT) |
| PATCH | `/participants/{id}` | `ParticipantRead` | Обновить (JWT) |
| DELETE| `/participants/{id}` | `{"ok": true}` | Удалить (JWT) |

### Teams

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/teams` | `List[TeamRead]` | Список команд |
| GET   | `/teams/{id}` | **`TeamReadFull`** | Команда с вложенными `participants` (m2m) и `tasks` (m2m) |
| POST  | `/teams` | `TeamRead` | Создать (JWT) |
| PATCH | `/teams/{id}` | `TeamRead` | Обновить (JWT) |
| DELETE| `/teams/{id}` | `{"ok": true}` | Удалить (JWT) |
| POST  | `/teams/{team_id}/members/{participant_id}?role=developer` | dict | Добавить участника в команду (JWT) |
| POST  | `/teams/{team_id}/submissions/{task_id}?repo_url=...&score=...` | dict | Сдать решение по задаче (JWT) |

### Tasks

| Метод | Путь | Ответ | Описание |
|---|---|---|---|
| GET   | `/tasks` | `List[TaskRead]` | Список задач |
| GET   | `/tasks/{id}` | **`TaskReadWithTeams`** | Задача с вложенными командами (m2m) |
| POST  | `/tasks` | `TaskRead` | Создать (JWT) |
| PATCH | `/tasks/{id}` | `TaskRead` | Обновить (JWT) |
| DELETE| `/tasks/{id}` | `{"ok": true}` | Удалить (JWT) |

## Код роутеров

### `app/routers/auth.py`

```python
"""Роутер регистрации и логина."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.security import create_access_token, hash_password, verify_password
from app.connection import get_session
from app.models.user import Token, User, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)) -> User:
    exists = session.exec(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )
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


@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)) -> Token:
    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)
```

### `app/routers/users.py`

```python
"""Пользовательские эндпоинты (требуют JWT)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.auth.security import hash_password, verify_password
from app.connection import get_session
from app.models.user import PasswordChange, User, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> List[User]:
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/me/change_password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    current_user.hashed_password = hash_password(data.new_password)
    session.add(current_user)
    session.commit()
```

### `app/routers/hackathons.py`

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.hackathon import (
    Hackathon, HackathonDefault, HackathonRead, HackathonReadFull,
)
from app.models.user import User

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.get("", response_model=List[HackathonRead])
def list_hackathons(session: Session = Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()


@router.get("/{hackathon_id}", response_model=HackathonReadFull)
def get_hackathon(
    hackathon_id: int, session: Session = Depends(get_session)
) -> Hackathon:
    """Возвращает хакатон с вложенными локацией, командами и задачами (o2m)."""
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return h


@router.post("", response_model=HackathonRead)
def create_hackathon(
    data: HackathonDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Hackathon:
    h = Hackathon.model_validate(data)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@router.patch("/{hackathon_id}", response_model=HackathonRead)
def update_hackathon(
    hackathon_id: int,
    data: HackathonDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Hackathon:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(h, k, v)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@router.delete("/{hackathon_id}")
def delete_hackathon(
    hackathon_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(h)
    session.commit()
    return {"ok": True}
```

### `app/routers/teams.py` (фрагменты m2m)

```python
@router.get("/{team_id}", response_model=TeamReadFull)
def get_team(team_id: int, session: Session = Depends(get_session)) -> Team:
    """Возвращает команду с вложенными участниками (m2m) и задачами (m2m)."""
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return t


@router.post("/{team_id}/members/{participant_id}")
def add_participant_to_team(
    team_id: int,
    participant_id: int,
    role: TeamRole = TeamRole.developer,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Participant, participant_id):
        raise HTTPException(status_code=404, detail="Participant not found")
    link = TeamParticipantLink(
        team_id=team_id, participant_id=participant_id, role=role
    )
    session.add(link)
    session.commit()
    return {"team_id": team_id, "participant_id": participant_id, "role": role.value}


@router.post("/{team_id}/submissions/{task_id}")
def submit_task(
    team_id: int,
    task_id: int,
    repo_url: str,
    score: int | None = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    submission = Submission(
        team_id=team_id, task_id=task_id, repo_url=repo_url, score=score
    )
    session.add(submission)
    session.commit()
    return {"team_id": team_id, "task_id": task_id, "repo_url": repo_url, "score": score}
```

Аналогичные файлы есть для `locations`, `participants` и `tasks`.
Их полный текст — в [`Lr_1/lab_1/app/routers/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_1/lab_1/app/routers/).

## Пример ответа с вложением

`GET /hackathons/1`:

```json
{
  "id": 1,
  "name": "ITMO Open Hack",
  "description": "Студенческий хакатон ИТМО",
  "status": "planned",
  "location_id": 1,
  "location": {
    "id": 1, "city": "Санкт-Петербург",
    "address": "Кронверкский пр., 49", "capacity": 200
  },
  "teams": [
    {"id": 1, "name": "Alpha", "hackathon_id": 1, "description": "..."}
  ],
  "tasks": [
    {"id": 1, "title": "Сервис уведомлений", "hackathon_id": 1, "...": "..."}
  ]
}
```

`GET /teams/1`:

```json
{
  "id": 1, "name": "Alpha", "hackathon_id": 1, "description": "...",
  "participants": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "tasks": [
    {"id": 3, "title": "Антифрод-движок", "hackathon_id": 2, "...": "..."}
  ]
}
```

## Навигация

- [← Подключение к БД](lab_1_db.md)
- [Авторизация и JWT →](lab_1_auth.md)
