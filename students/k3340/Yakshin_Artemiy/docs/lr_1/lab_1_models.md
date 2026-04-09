# Модели данных

Все модели реализованы с помощью **SQLModel** (надстройка над SQLAlchemy)
и разнесены по отдельным файлам в `app/models/`. Критерий ЛР (≥5 таблиц,
o2m + m2m, ассоциативная сущность с характеризующим связь полем)
выполнен.

## Перечисления — `app/models/enums.py`

```python
from enum import Enum


class HackathonStatus(str, Enum):
    planned = "planned"
    ongoing = "ongoing"
    finished = "finished"


class TeamRole(str, Enum):
    lead = "lead"
    developer = "developer"
    designer = "designer"
    pm = "pm"
    analyst = "analyst"
```

## Ассоциативные сущности — `app/models/associations.py`

Здесь важно: обе ассоциативные таблицы содержат **поля, характеризующие
связь**, помимо ссылок на связанные сущности.

```python
"""Ассоциативные сущности для many-to-many связей."""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

from app.models.enums import TeamRole


class TeamParticipantLink(SQLModel, table=True):
    """Ассоциативная сущность Team <-> Participant.

    Поля, характеризующие связь: role, joined_at.
    """
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    participant_id: Optional[int] = Field(
        default=None, foreign_key="participant.id", primary_key=True
    )
    role: Optional[TeamRole] = Field(default=TeamRole.developer)
    joined_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Submission(SQLModel, table=True):
    """Ассоциативная сущность Team <-> Task: сдача работы команды по задаче.

    Поля, характеризующие связь: repo_url, score, submitted_at.
    """
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
    repo_url: Optional[str] = None
    score: Optional[int] = None
    submitted_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

## `Location` — `app/models/location.py`

```python
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.hackathon import Hackathon


class LocationDefault(SQLModel):
    city: str
    address: str
    capacity: int


class Location(LocationDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathons: List["Hackathon"] = Relationship(back_populates="location")


class LocationRead(LocationDefault):
    id: int
```

## `Hackathon` — `app/models/hackathon.py`

```python
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import HackathonStatus
from app.models.location import Location, LocationRead

if TYPE_CHECKING:
    from app.models.task import Task, TaskRead
    from app.models.team import Team, TeamRead


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


class HackathonRead(HackathonDefault):
    id: int


class HackathonReadFull(HackathonRead):
    """Хакатон с вложенными связанными сущностями (o2m)."""
    location: Optional[LocationRead] = None
    teams: List["TeamRead"] = []
    tasks: List["TaskRead"] = []
```

## `Team` — `app/models/team.py`

```python
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import Submission, TeamParticipantLink

if TYPE_CHECKING:
    from app.models.hackathon import Hackathon
    from app.models.participant import Participant, ParticipantRead
    from app.models.task import Task, TaskRead


class TeamDefault(SQLModel):
    name: str
    description: Optional[str] = None
    hackathon_id: Optional[int] = Field(default=None, foreign_key="hackathon.id")


class Team(TeamDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathon: Optional["Hackathon"] = Relationship(back_populates="teams")
    participants: List["Participant"] = Relationship(
        back_populates="teams", link_model=TeamParticipantLink
    )
    tasks: List["Task"] = Relationship(
        back_populates="teams", link_model=Submission
    )


class TeamRead(TeamDefault):
    id: int


class TeamReadFull(TeamRead):
    """Команда с вложенными участниками (m2m) и задачами (m2m)."""
    participants: List["ParticipantRead"] = []
    tasks: List["TaskRead"] = []
```

## `Participant` — `app/models/participant.py`

```python
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import TeamParticipantLink

if TYPE_CHECKING:
    from app.models.team import Team, TeamRead


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


class ParticipantRead(ParticipantDefault):
    id: int


class ParticipantReadWithTeams(ParticipantRead):
    teams: List["TeamRead"] = []
```

## `Task` — `app/models/task.py`

```python
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.associations import Submission

if TYPE_CHECKING:
    from app.models.hackathon import Hackathon
    from app.models.team import Team, TeamRead


class TaskDefault(SQLModel):
    title: str
    description: str
    requirements: str
    evaluation_criteria: str
    hackathon_id: Optional[int] = Field(default=None, foreign_key="hackathon.id")


class Task(TaskDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hackathon: Optional["Hackathon"] = Relationship(back_populates="tasks")
    teams: List["Team"] = Relationship(
        back_populates="tasks", link_model=Submission
    )


class TaskRead(TaskDefault):
    id: int


class TaskReadWithTeams(TaskRead):
    teams: List["TeamRead"] = []
```

## `User` — `app/models/user.py`

```python
"""Модель пользователя для авторизации."""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


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

## Агрегатор `app/models/__init__.py`

Нужен для того, чтобы:

1. Все таблицы попали в `SQLModel.metadata` (важно для `init_db` и Alembic).
2. Резолвить forward references для read-моделей с вложенными объектами
   (`model_rebuild()`).

```python
from app.models.associations import Submission, TeamParticipantLink
from app.models.enums import HackathonStatus, TeamRole
from app.models.hackathon import (
    Hackathon, HackathonDefault, HackathonRead, HackathonReadFull,
)
from app.models.location import Location, LocationDefault, LocationRead
from app.models.participant import (
    Participant, ParticipantDefault, ParticipantRead, ParticipantReadWithTeams,
)
from app.models.task import Task, TaskDefault, TaskRead, TaskReadWithTeams
from app.models.team import Team, TeamDefault, TeamRead, TeamReadFull
from app.models.user import (
    PasswordChange, Token, User, UserBase, UserCreate, UserLogin, UserRead,
)

# Резолв forward references для read-моделей с вложенными объектами
HackathonReadFull.model_rebuild()
TeamReadFull.model_rebuild()
ParticipantReadWithTeams.model_rebuild()
TaskReadWithTeams.model_rebuild()
```

## Схема связей

```
Location (1) ──< (M) Hackathon (1) ──< (M) Team
                              └──< (M) Task

Team (M) ──< TeamParticipantLink (role) >── (M) Participant
Team (M) ──< Submission (score, repo_url) >── (M) Task
```

## Навигация

- [← Структура проекта](lab_1_structure.md)
- [Подключение к БД →](lab_1_db.md)
