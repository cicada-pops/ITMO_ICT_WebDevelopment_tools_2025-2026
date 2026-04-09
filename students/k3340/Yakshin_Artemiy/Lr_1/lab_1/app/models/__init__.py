"""Агрегатор моделей — импортирует все таблицы,
чтобы они были зарегистрированы в SQLModel.metadata,
и резолвит forward references в Pydantic-моделях."""
from app.models.associations import Submission, TeamParticipantLink
from app.models.enums import HackathonStatus, TeamRole
from app.models.hackathon import (
    Hackathon,
    HackathonDefault,
    HackathonRead,
    HackathonReadFull,
)
from app.models.location import Location, LocationDefault, LocationRead
from app.models.participant import (
    Participant,
    ParticipantDefault,
    ParticipantRead,
    ParticipantReadWithTeams,
)
from app.models.task import Task, TaskDefault, TaskRead, TaskReadWithTeams
from app.models.team import Team, TeamDefault, TeamRead, TeamReadFull
from app.models.user import (
    PasswordChange,
    Token,
    User,
    UserBase,
    UserCreate,
    UserLogin,
    UserRead,
)

# Резолв forward references для read-моделей с вложенными объектами
HackathonReadFull.model_rebuild()
TeamReadFull.model_rebuild()
ParticipantReadWithTeams.model_rebuild()
TaskReadWithTeams.model_rebuild()

__all__ = [
    "HackathonStatus",
    "TeamRole",
    "TeamParticipantLink",
    "Submission",
    "Location",
    "LocationDefault",
    "LocationRead",
    "Hackathon",
    "HackathonDefault",
    "HackathonRead",
    "HackathonReadFull",
    "Participant",
    "ParticipantDefault",
    "ParticipantRead",
    "ParticipantReadWithTeams",
    "Team",
    "TeamDefault",
    "TeamRead",
    "TeamReadFull",
    "Task",
    "TaskDefault",
    "TaskRead",
    "TaskReadWithTeams",
    "User",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserLogin",
    "PasswordChange",
    "Token",
]
