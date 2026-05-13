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
