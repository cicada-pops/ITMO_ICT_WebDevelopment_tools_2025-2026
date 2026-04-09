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
