from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.location import Location, LocationDefault, LocationRead
from app.models.user import User

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=List[LocationRead])
def list_locations(session: Session = Depends(get_session)) -> List[Location]:
    return session.exec(select(Location)).all()


@router.get("/{location_id}", response_model=LocationRead)
def get_location(
    location_id: int, session: Session = Depends(get_session)
) -> Location:
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.post("", response_model=LocationRead)
def create_location(
    data: LocationDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Location:
    loc = Location.model_validate(data)
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return loc


@router.patch("/{location_id}", response_model=LocationRead)
def update_location(
    location_id: int,
    data: LocationDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Location:
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return loc


@router.delete("/{location_id}")
def delete_location(
    location_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    session.delete(loc)
    session.commit()
    return {"ok": True}
