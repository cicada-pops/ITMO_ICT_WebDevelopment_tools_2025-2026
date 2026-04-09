# Практика 1.2 — SQLModel + PostgreSQL

## Задание

1. Пошагово реализовать подключение к БД, API и модели на основе своего варианта.
2. Сделать модели и API для `many-to-many` связей с **вложенным отображением**.

## Результат

Перешли с временной базы на реальную PostgreSQL через `SQLModel`. Добавили:

- 6 таблиц: `Location`, `Hackathon`, `Team`, `Participant`, `Task` и две
  ассоциативные (`TeamParticipantLink`, `Submission`);
- связи one-to-many (Hackathon → Team, Hackathon → Task, Location → Hackathon);
- связи many-to-many (Team ↔ Participant, Team ↔ Task);
- полноценный CRUD через сессии ORM;
- GET-запросы с вложенными связанными сущностями через `response_model`.

## Подключение к БД

`practice_1_2/connection.py`:

```python
from sqlmodel import Session, SQLModel, create_engine

db_url = "postgresql://postgres:123@localhost/hackathons_db"
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Инициализация таблиц при старте в `main.py`:

```python
@app.on_event("startup")
def on_startup() -> None:
    init_db()
```

## Модели SQLModel

`practice_1_2/models.py`:

```python
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class HackathonStatus(str, Enum):
    planned = "planned"
    ongoing = "ongoing"
    finished = "finished"


# ---------- Ассоциативные сущности (many-to-many) ----------

class TeamParticipantLink(SQLModel, table=True):
    """Ассоциативная сущность Team <-> Participant с полем role."""
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
    participant_id: Optional[int] = Field(default=None, foreign_key="participant.id", primary_key=True)
    role: Optional[str] = None   # поле, характеризующее связь


class Submission(SQLModel, table=True):
    """Ассоциативная сущность Team <-> Task: сдача работы с оценкой."""
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    repo_url: Optional[str] = None
    score: Optional[int] = None


# ---------- Основные таблицы ----------

class LocationDefault(SQLModel):
    city: str
    address: str
    capacity: int


class Location(LocationDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathons: List["Hackathon"] = Relationship(back_populates="location")


class HackathonDefault(SQLModel):
    name: str
    description: str
    status: HackathonStatus = HackathonStatus.planned
    location_id: Optional[int] = Field(default=None, foreign_key="location.id")


class Hackathon(HackathonDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location: Optional[Location] = Relationship(back_populates="hackathons")
    teams: List["Team"] = Relationship(back_populates="hackathon")
    tasks: List["Task"] = Relationship(back_populates="hackathon")


class ParticipantDefault(SQLModel):
    name: str
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None


class Participant(ParticipantDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teams: List["Team"] = Relationship(
        back_populates="participants", link_model=TeamParticipantLink
    )


class TeamDefault(SQLModel):
    name: str
    description: Optional[str] = None
    hackathon_id: Optional[int] = Field(default=None, foreign_key="hackathon.id")


class Team(TeamDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathon: Optional[Hackathon] = Relationship(back_populates="teams")
    participants: List[Participant] = Relationship(
        back_populates="teams", link_model=TeamParticipantLink
    )
    tasks: List["Task"] = Relationship(
        back_populates="teams", link_model=Submission
    )


class TaskDefault(SQLModel):
    title: str
    description: str
    requirements: str
    evaluation_criteria: str
    hackathon_id: Optional[int] = Field(default=None, foreign_key="hackathon.id")


class Task(TaskDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathon: Optional[Hackathon] = Relationship(back_populates="tasks")
    teams: List[Team] = Relationship(back_populates="tasks", link_model=Submission)
```

### Read-модели с вложением

```python
class HackathonWithRelations(HackathonDefault):
    id: int
    location: Optional[Location] = None
    teams: List[TeamDefault] = []
    tasks: List[TaskDefault] = []


class TeamWithRelations(TeamDefault):
    id: int
    participants: List[ParticipantDefault] = []
    tasks: List[TaskDefault] = []


class ParticipantWithTeams(ParticipantDefault):
    id: int
    teams: List[TeamDefault] = []


class TaskWithTeams(TaskDefault):
    id: int
    teams: List[TeamDefault] = []
```

## Ключевые эндпоинты

### CRUD c ORM (пример для `Hackathon`)

```python
@app.get("/hackathons", response_model=List[Hackathon])
def hackathons_list(session=Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()


@app.get("/hackathon/{hackathon_id}", response_model=HackathonWithRelations)
def hackathon_get(hackathon_id: int, session=Depends(get_session)) -> Hackathon:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return h


@app.post("/hackathon")
def hackathon_create(
    hackathon: HackathonDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Hackathon}):
    h = Hackathon.model_validate(hackathon)
    session.add(h)
    session.commit()
    session.refresh(h)
    return {"status": 200, "data": h}


@app.patch("/hackathon/{hackathon_id}", response_model=Hackathon)
def hackathon_update(hackathon_id: int, hackathon: HackathonDefault, session=Depends(get_session)) -> Hackathon:
    db_h = session.get(Hackathon, hackathon_id)
    if not db_h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    for k, v in hackathon.model_dump(exclude_unset=True).items():
        setattr(db_h, k, v)
    session.add(db_h)
    session.commit()
    session.refresh(db_h)
    return db_h


@app.delete("/hackathon/{hackathon_id}")
def hackathon_delete(hackathon_id: int, session=Depends(get_session)) -> dict:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(h)
    session.commit()
    return {"ok": True}
```

### Many-to-many эндпоинты

```python
@app.post("/team/{team_id}/add_participant/{participant_id}")
def team_add_participant(
    team_id: int, participant_id: int, role: str,
    session: Session = Depends(get_session),
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
    return {"status": 200, "data": {...}}


@app.post("/team/{team_id}/submit/{task_id}")
def team_submit_task(
    team_id: int, task_id: int, repo_url: str, score: int | None = None,
    session: Session = Depends(get_session),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    sub = Submission(team_id=team_id, task_id=task_id, repo_url=repo_url, score=score)
    session.add(sub)
    session.commit()
    return {"status": 200, "data": {...}}
```

### GET с вложенными объектами

`GET /team/{team_id}` возвращает команду с вложенным списком участников
(m2m) и задач (m2m):

```json
{
  "id": 1,
  "name": "Team Alpha",
  "hackathon_id": 1,
  "description": "Топ команда",
  "participants": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "tasks": [
    {"id": 3, "title": "Антифрод-движок", "description": "..."}
  ]
}
```

## Таблица эндпоинтов

CRUD для всех сущностей: `Location`, `Hackathon`, `Team`, `Participant`, `Task`.
Плюс два m2m-эндпоинта: `POST /team/{team_id}/add_participant/{participant_id}`,
`POST /team/{team_id}/submit/{task_id}`.

## Ссылки

- Исходный код — [`Lr_1/practice_1_2/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_1/practice_1_2/)
- [← Практика 1.1](practice_1_1.md) | [Далее: Практика 1.3 →](practice_1_3.md)
