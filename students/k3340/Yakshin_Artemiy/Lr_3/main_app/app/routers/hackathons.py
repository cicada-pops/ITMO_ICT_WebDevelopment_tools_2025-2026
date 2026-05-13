from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.hackathon import (
    Hackathon,
    HackathonDefault,
    HackathonRead,
    HackathonReadFull,
)
from app.models.user import User

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.get("", response_model=List[HackathonRead])
def list_hackathons(session: Session = Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()


@router.get("/{hackathon_id}", response_model=HackathonReadFull)
def get_hackathon(
    hackathon_id: int, session: Session = Depends(get_session)
) -> Hackathon:
    """Возвращает хакатон с вложенными локацией, командами и задачами (o2m)."""
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return h


@router.post("", response_model=HackathonRead)
def create_hackathon(
    data: HackathonDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Hackathon:
    h = Hackathon.model_validate(data)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@router.patch("/{hackathon_id}", response_model=HackathonRead)
def update_hackathon(
    hackathon_id: int,
    data: HackathonDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Hackathon:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(h, k, v)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h


@router.delete("/{hackathon_id}")
def delete_hackathon(
    hackathon_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(h)
    session.commit()
    return {"ok": True}
