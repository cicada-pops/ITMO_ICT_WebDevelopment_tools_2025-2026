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
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    participant_id: Optional[int] = Field(
        default=None, foreign_key="participant.id", primary_key=True
    )
    role: Optional[str] = None  # роль в команде: developer / designer / pm


class Submission(SQLModel, table=True):
    """Ассоциативная сущность Team <-> Task: сдача работы с оценкой."""
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
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
    teams: List[Team] = Relationship(
        back_populates="tasks", link_model=Submission
    )


# ---------- Response-модели с вложенными объектами ----------

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
