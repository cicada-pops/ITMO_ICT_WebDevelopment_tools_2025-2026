from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.associations import Submission, TeamParticipantLink
from app.models.enums import TeamRole
from app.models.participant import Participant
from app.models.task import Task
from app.models.team import Team, TeamDefault, TeamRead, TeamReadFull
from app.models.user import User

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=List[TeamRead])
def list_teams(session: Session = Depends(get_session)) -> List[Team]:
    return session.exec(select(Team)).all()


@router.get("/{team_id}", response_model=TeamReadFull)
def get_team(team_id: int, session: Session = Depends(get_session)) -> Team:
    """Возвращает команду с вложенными участниками (m2m) и задачами (m2m)."""
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return t


@router.post("", response_model=TeamRead)
def create_team(
    data: TeamDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Team:
    t = Team.model_validate(data)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    data: TeamDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Team:
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(t)
    session.commit()
    return {"ok": True}


# ---------- Управление связями m2m ----------

@router.post("/{team_id}/members/{participant_id}")
def add_participant_to_team(
    team_id: int,
    participant_id: int,
    role: TeamRole = TeamRole.developer,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Participant, participant_id):
        raise HTTPException(status_code=404, detail="Participant not found")
    link = TeamParticipantLink(
        team_id=team_id, participant_id=participant_id, role=role
    )
    session.add(link)
    session.commit()
    return {
        "team_id": team_id,
        "participant_id": participant_id,
        "role": role.value,
    }


@router.post("/{team_id}/submissions/{task_id}")
def submit_task(
    team_id: int,
    task_id: int,
    repo_url: str,
    score: Optional[int] = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    submission = Submission(
        team_id=team_id, task_id=task_id, repo_url=repo_url, score=score
    )
    session.add(submission)
    session.commit()
    return {
        "team_id": team_id,
        "task_id": task_id,
        "repo_url": repo_url,
        "score": score,
    }
