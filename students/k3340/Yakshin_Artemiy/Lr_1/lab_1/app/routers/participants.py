from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.participant import (
    Participant,
    ParticipantDefault,
    ParticipantRead,
    ParticipantReadWithTeams,
)
from app.models.user import User

router = APIRouter(prefix="/participants", tags=["participants"])


@router.get("", response_model=List[ParticipantRead])
def list_participants(session: Session = Depends(get_session)) -> List[Participant]:
    return session.exec(select(Participant)).all()


@router.get("/{participant_id}", response_model=ParticipantReadWithTeams)
def get_participant(
    participant_id: int, session: Session = Depends(get_session)
) -> Participant:
    p = session.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    return p


@router.post("", response_model=ParticipantRead)
def create_participant(
    data: ParticipantDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Participant:
    p = Participant.model_validate(data)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@router.patch("/{participant_id}", response_model=ParticipantRead)
def update_participant(
    participant_id: int,
    data: ParticipantDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Participant:
    p = session.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@router.delete("/{participant_id}")
def delete_participant(
    participant_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    p = session.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    session.delete(p)
    session.commit()
    return {"ok": True}
