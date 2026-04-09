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
