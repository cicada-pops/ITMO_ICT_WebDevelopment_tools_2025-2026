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
