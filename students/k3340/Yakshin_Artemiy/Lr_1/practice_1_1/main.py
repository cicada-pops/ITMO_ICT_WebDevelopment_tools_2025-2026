from typing import List

from fastapi import FastAPI, HTTPException

from models import (
    Hackathon,
    HackathonResponse,
    HackathonStatus,
    Location,
    Task,
    TaskResponse,
)

app = FastAPI(title="Hackathons (practice 1.1)")


# Временная БД главной сущности с одиночным вложенным объектом (Location)
# и списком вложенных объектов (Task)
temp_bd: List[dict] = [
    {
        "id": 1,
        "name": "ITMO Open Hack",
        "description": "Студенческий хакатон ИТМО",
        "status": HackathonStatus.planned,
        "location": {
            "id": 1,
            "city": "Санкт-Петербург",
            "address": "Кронверкский пр., 49",
            "capacity": 200,
        },
        "tasks": [
            {
                "id": 1,
                "title": "Сервис уведомлений",
                "description": "Разработать сервис push-уведомлений",
                "requirements": "Python, FastAPI",
                "evaluation_criteria": "Работоспособность, архитектура",
            },
            {
                "id": 2,
                "title": "ML-классификатор",
                "description": "Классификация заявок участников",
                "requirements": "Python, sklearn",
                "evaluation_criteria": "Точность, F1",
            },
        ],
    },
    {
        "id": 2,
        "name": "FinTech Sprint",
        "description": "Хакатон по финансовым технологиям",
        "status": HackathonStatus.ongoing,
        "location": {
            "id": 2,
            "city": "Москва",
            "address": "ул. Льва Толстого, 16",
            "capacity": 350,
        },
        "tasks": [
            {
                "id": 3,
                "title": "Антифрод-движок",
                "description": "Прототип антифрод-системы",
                "requirements": "Python, ML",
                "evaluation_criteria": "Полнота, скорость",
            }
        ],
    },
    {
        "id": 3,
        "name": "GreenTech Hack",
        "description": "Экология и устойчивое развитие",
        "status": HackathonStatus.finished,
        "location": {
            "id": 1,
            "city": "Санкт-Петербург",
            "address": "Кронверкский пр., 49",
            "capacity": 200,
        },
        "tasks": [],
    },
]


# ---------- Hackathon CRUD ----------

@app.get("/hackathons", response_model=List[Hackathon])
def hackathons_list() -> List[Hackathon]:
    return [Hackathon(**h) for h in temp_bd]


@app.get("/hackathon/{hackathon_id}", response_model=Hackathon)
def hackathon_get(hackathon_id: int) -> Hackathon:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            return Hackathon(**h)
    raise HTTPException(status_code=404, detail="Hackathon not found")


@app.post("/hackathon", response_model=HackathonResponse)
def hackathon_create(hackathon: Hackathon) -> HackathonResponse:
    temp_bd.append(hackathon.model_dump())
    return {"status": 200, "data": hackathon}


@app.put("/hackathon/{hackathon_id}", response_model=Hackathon)
def hackathon_update(hackathon_id: int, hackathon: Hackathon) -> Hackathon:
    for i, h in enumerate(temp_bd):
        if h["id"] == hackathon_id:
            temp_bd[i] = hackathon.model_dump()
            return hackathon
    raise HTTPException(status_code=404, detail="Hackathon not found")


@app.delete("/hackathon/{hackathon_id}")
def hackathon_delete(hackathon_id: int) -> dict:
    for i, h in enumerate(temp_bd):
        if h["id"] == hackathon_id:
            temp_bd.pop(i)
            return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Hackathon not found")


# ---------- Вложенный объект (Task) — отдельный CRUD ----------

@app.get("/hackathon/{hackathon_id}/tasks", response_model=List[Task])
def tasks_list(hackathon_id: int) -> List[Task]:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            return [Task(**t) for t in h.get("tasks", [])]
    raise HTTPException(status_code=404, detail="Hackathon not found")


@app.get("/hackathon/{hackathon_id}/task/{task_id}", response_model=Task)
def task_get(hackathon_id: int, task_id: int) -> Task:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            for t in h.get("tasks", []):
                if t["id"] == task_id:
                    return Task(**t)
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/hackathon/{hackathon_id}/task", response_model=TaskResponse)
def task_create(hackathon_id: int, task: Task) -> TaskResponse:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            h.setdefault("tasks", []).append(task.model_dump())
            return {"status": 200, "data": task}
    raise HTTPException(status_code=404, detail="Hackathon not found")


@app.put("/hackathon/{hackathon_id}/task/{task_id}", response_model=Task)
def task_update(hackathon_id: int, task_id: int, task: Task) -> Task:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            for i, t in enumerate(h.get("tasks", [])):
                if t["id"] == task_id:
                    h["tasks"][i] = task.model_dump()
                    return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/hackathon/{hackathon_id}/task/{task_id}")
def task_delete(hackathon_id: int, task_id: int) -> dict:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            for i, t in enumerate(h.get("tasks", [])):
                if t["id"] == task_id:
                    h["tasks"].pop(i)
                    return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Task not found")


# ---------- Локация (одиночный вложенный объект) ----------

@app.get("/hackathon/{hackathon_id}/location", response_model=Location)
def location_get(hackathon_id: int) -> Location:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            return Location(**h["location"])
    raise HTTPException(status_code=404, detail="Hackathon not found")


@app.put("/hackathon/{hackathon_id}/location", response_model=Location)
def location_update(hackathon_id: int, location: Location) -> Location:
    for h in temp_bd:
        if h["id"] == hackathon_id:
            h["location"] = location.model_dump()
            return location
    raise HTTPException(status_code=404, detail="Hackathon not found")
