from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from typing_extensions import TypedDict


class HackathonStatus(str, Enum):
    planned = "planned"
    ongoing = "ongoing"
    finished = "finished"


class Location(BaseModel):
    id: int
    city: str
    address: str
    capacity: int


class Task(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    evaluation_criteria: str


class Hackathon(BaseModel):
    id: int
    name: str
    description: str
    status: HackathonStatus
    location: Location
    tasks: Optional[List[Task]] = []


class HackathonResponse(TypedDict):
    status: int
    data: Hackathon


class TaskResponse(TypedDict):
    status: int
    data: Task
