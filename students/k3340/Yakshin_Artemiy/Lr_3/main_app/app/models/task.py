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
