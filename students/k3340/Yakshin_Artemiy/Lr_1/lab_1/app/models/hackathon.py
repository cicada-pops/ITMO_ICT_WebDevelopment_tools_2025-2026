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
