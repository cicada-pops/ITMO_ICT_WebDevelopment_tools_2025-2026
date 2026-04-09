from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from connection import get_session, init_db
from models import (
    Hackathon,
    HackathonDefault,
    HackathonWithRelations,
    Location,
    LocationDefault,
    Participant,
    ParticipantDefault,
    ParticipantWithTeams,
    Submission,
    Task,
    TaskDefault,
    TaskWithTeams,
    Team,
    TeamDefault,
    TeamParticipantLink,
    TeamWithRelations,
)

app = FastAPI(title="Hackathons (practice 1.2)")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# =====================================================================
#                             LOCATION
# =====================================================================

@app.get("/locations", response_model=List[Location])
def locations_list(session: Session = Depends(get_session)) -> List[Location]:
    return session.exec(select(Location)).all()


@app.get("/location/{location_id}", response_model=Location)
def location_get(location_id: int, session: Session = Depends(get_session)) -> Location:
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@app.post("/location")
def location_create(
    location: LocationDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Location}):
    loc = Location.model_validate(location)
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return {"status": 200, "data": loc}


@app.patch("/location/{location_id}", response_model=Location)
def location_update(
    location_id: int,
    location: LocationDefault,
    session: Session = Depends(get_session),
) -> Location:
    db_loc = session.get(Location, location_id)
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for k, v in location.model_dump(exclude_unset=True).items():
        setattr(db_loc, k, v)
    session.add(db_loc)
    session.commit()
    session.refresh(db_loc)
    return db_loc


@app.delete("/location/{location_id}")
def location_delete(location_id: int, session: Session = Depends(get_session)) -> dict:
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    session.delete(loc)
    session.commit()
    return {"ok": True}


# =====================================================================
#                             HACKATHON
# =====================================================================

@app.get("/hackathons", response_model=List[Hackathon])
def hackathons_list(session: Session = Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()


@app.get("/hackathon/{hackathon_id}", response_model=HackathonWithRelations)
def hackathon_get(
    hackathon_id: int, session: Session = Depends(get_session)
) -> Hackathon:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return h


@app.post("/hackathon")
def hackathon_create(
    hackathon: HackathonDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Hackathon}):
    h = Hackathon.model_validate(hackathon)
    session.add(h)
    session.commit()
    session.refresh(h)
    return {"status": 200, "data": h}


@app.patch("/hackathon/{hackathon_id}", response_model=Hackathon)
def hackathon_update(
    hackathon_id: int,
    hackathon: HackathonDefault,
    session: Session = Depends(get_session),
) -> Hackathon:
    db_h = session.get(Hackathon, hackathon_id)
    if not db_h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    for k, v in hackathon.model_dump(exclude_unset=True).items():
        setattr(db_h, k, v)
    session.add(db_h)
    session.commit()
    session.refresh(db_h)
    return db_h


@app.delete("/hackathon/{hackathon_id}")
def hackathon_delete(
    hackathon_id: int, session: Session = Depends(get_session)
) -> dict:
    h = session.get(Hackathon, hackathon_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(h)
    session.commit()
    return {"ok": True}


# =====================================================================
#                             PARTICIPANT
# =====================================================================

@app.get("/participants", response_model=List[Participant])
def participants_list(session: Session = Depends(get_session)) -> List[Participant]:
    return session.exec(select(Participant)).all()


@app.get("/participant/{participant_id}", response_model=ParticipantWithTeams)
def participant_get(
    participant_id: int, session: Session = Depends(get_session)
) -> Participant:
    p = session.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    return p


@app.post("/participant")
def participant_create(
    participant: ParticipantDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Participant}):
    p = Participant.model_validate(participant)
    session.add(p)
    session.commit()
    session.refresh(p)
    return {"status": 200, "data": p}


@app.patch("/participant/{participant_id}", response_model=Participant)
def participant_update(
    participant_id: int,
    participant: ParticipantDefault,
    session: Session = Depends(get_session),
) -> Participant:
    db_p = session.get(Participant, participant_id)
    if not db_p:
        raise HTTPException(status_code=404, detail="Participant not found")
    for k, v in participant.model_dump(exclude_unset=True).items():
        setattr(db_p, k, v)
    session.add(db_p)
    session.commit()
    session.refresh(db_p)
    return db_p


@app.delete("/participant/{participant_id}")
def participant_delete(
    participant_id: int, session: Session = Depends(get_session)
) -> dict:
    p = session.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    session.delete(p)
    session.commit()
    return {"ok": True}


# =====================================================================
#                                TEAM
# =====================================================================

@app.get("/teams", response_model=List[Team])
def teams_list(session: Session = Depends(get_session)) -> List[Team]:
    return session.exec(select(Team)).all()


@app.get("/team/{team_id}", response_model=TeamWithRelations)
def team_get(team_id: int, session: Session = Depends(get_session)) -> Team:
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return t


@app.post("/team")
def team_create(
    team: TeamDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Team}):
    t = Team.model_validate(team)
    session.add(t)
    session.commit()
    session.refresh(t)
    return {"status": 200, "data": t}


@app.patch("/team/{team_id}", response_model=Team)
def team_update(
    team_id: int, team: TeamDefault, session: Session = Depends(get_session)
) -> Team:
    db_t = session.get(Team, team_id)
    if not db_t:
        raise HTTPException(status_code=404, detail="Team not found")
    for k, v in team.model_dump(exclude_unset=True).items():
        setattr(db_t, k, v)
    session.add(db_t)
    session.commit()
    session.refresh(db_t)
    return db_t


@app.delete("/team/{team_id}")
def team_delete(team_id: int, session: Session = Depends(get_session)) -> dict:
    t = session.get(Team, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(t)
    session.commit()
    return {"ok": True}


# =====================================================================
#                                TASK
# =====================================================================

@app.get("/tasks", response_model=List[Task])
def tasks_list(session: Session = Depends(get_session)) -> List[Task]:
    return session.exec(select(Task)).all()


@app.get("/task/{task_id}", response_model=TaskWithTeams)
def task_get(task_id: int, session: Session = Depends(get_session)) -> Task:
    t = session.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@app.post("/task")
def task_create(
    task: TaskDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Task}):
    t = Task.model_validate(task)
    session.add(t)
    session.commit()
    session.refresh(t)
    return {"status": 200, "data": t}


@app.patch("/task/{task_id}", response_model=Task)
def task_update(
    task_id: int, task: TaskDefault, session: Session = Depends(get_session)
) -> Task:
    db_t = session.get(Task, task_id)
    if not db_t:
        raise HTTPException(status_code=404, detail="Task not found")
    for k, v in task.model_dump(exclude_unset=True).items():
        setattr(db_t, k, v)
    session.add(db_t)
    session.commit()
    session.refresh(db_t)
    return db_t


@app.delete("/task/{task_id}")
def task_delete(task_id: int, session: Session = Depends(get_session)) -> dict:
    t = session.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(t)
    session.commit()
    return {"ok": True}


# =====================================================================
#             MANY-TO-MANY: добавление участника в команду
# =====================================================================

@app.post("/team/{team_id}/add_participant/{participant_id}")
def team_add_participant(
    team_id: int,
    participant_id: int,
    role: str,
    session: Session = Depends(get_session),
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
    return {"status": 200, "data": {"team_id": team_id, "participant_id": participant_id, "role": role}}


@app.post("/team/{team_id}/submit/{task_id}")
def team_submit_task(
    team_id: int,
    task_id: int,
    repo_url: str,
    score: int | None = None,
    session: Session = Depends(get_session),
) -> dict:
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    if not session.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    sub = Submission(team_id=team_id, task_id=task_id, repo_url=repo_url, score=score)
    session.add(sub)
    session.commit()
    return {
        "status": 200,
        "data": {
            "team_id": team_id,
            "task_id": task_id,
            "repo_url": repo_url,
            "score": score,
        },
    }
