# Практика 1.1 — FastAPI + Pydantic + временная БД

## Задание

1. Сделать временную базу для главной таблицы (2–3 записи), по аналогии с
   практикой: должен быть одиночный вложенный объект и список вложенных объектов.
2. Выполнить действия из практики для своего проекта.
3. Сделать модели и API для вложенного объекта.

## Результат

- Главная сущность — `Hackathon`.
- Одиночный вложенный объект — `Location`.
- Список вложенных объектов — `tasks: List[Task]`.
- Полный CRUD для `Hackathon`, отдельный CRUD для `Task`, GET/PUT для `Location`.

## Pydantic-модели

`practice_1_1/models.py`:

```python
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
```

## Временная БД

Фрагмент `practice_1_1/main.py`:

```python
temp_bd: List[dict] = [
    {
        "id": 1,
        "name": "ITMO Open Hack",
        "description": "Студенческий хакатон ИТМО",
        "status": HackathonStatus.planned,
        "location": {
            "id": 1, "city": "Санкт-Петербург",
            "address": "Кронверкский пр., 49", "capacity": 200,
        },
        "tasks": [
            {"id": 1, "title": "Сервис уведомлений", ...},
            {"id": 2, "title": "ML-классификатор", ...},
        ],
    },
    # ещё 2 записи
]
```

## Эндпоинты

### Hackathon (главная сущность)

```python
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
def hackathon_update(hackathon_id: int, hackathon: Hackathon) -> Hackathon: ...


@app.delete("/hackathon/{hackathon_id}")
def hackathon_delete(hackathon_id: int) -> dict: ...
```

### Task (вложенная сущность)

```python
@app.get("/hackathon/{hackathon_id}/tasks", response_model=List[Task])
def tasks_list(hackathon_id: int) -> List[Task]: ...


@app.get("/hackathon/{hackathon_id}/task/{task_id}", response_model=Task)
def task_get(hackathon_id: int, task_id: int) -> Task: ...


@app.post("/hackathon/{hackathon_id}/task", response_model=TaskResponse)
def task_create(hackathon_id: int, task: Task) -> TaskResponse: ...


@app.put("/hackathon/{hackathon_id}/task/{task_id}", response_model=Task)
def task_update(hackathon_id: int, task_id: int, task: Task) -> Task: ...


@app.delete("/hackathon/{hackathon_id}/task/{task_id}")
def task_delete(hackathon_id: int, task_id: int) -> dict: ...
```

### Location (одиночный вложенный объект)

```python
@app.get("/hackathon/{hackathon_id}/location", response_model=Location)
def location_get(hackathon_id: int) -> Location: ...


@app.put("/hackathon/{hackathon_id}/location", response_model=Location)
def location_update(hackathon_id: int, location: Location) -> Location: ...
```

## Таблица эндпоинтов

| Метод  | Путь | Назначение |
|--------|------|------------|
| GET    | `/hackathons` | список хакатонов |
| GET    | `/hackathon/{id}` | получить хакатон |
| POST   | `/hackathon` | создать хакатон |
| PUT    | `/hackathon/{id}` | обновить хакатон |
| DELETE | `/hackathon/{id}` | удалить хакатон |
| GET    | `/hackathon/{id}/tasks` | список задач |
| GET    | `/hackathon/{id}/task/{task_id}` | получить задачу |
| POST   | `/hackathon/{id}/task` | создать задачу |
| PUT    | `/hackathon/{id}/task/{task_id}` | обновить задачу |
| DELETE | `/hackathon/{id}/task/{task_id}` | удалить задачу |
| GET    | `/hackathon/{id}/location` | получить локацию |
| PUT    | `/hackathon/{id}/location` | обновить локацию |

## Запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger: <http://127.0.0.1:8000/docs>

## Ссылки

- Исходный код — [`Lr_1/practice_1_1/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_1/practice_1_1/)
- [Далее: Практика 1.2 →](practice_1_2.md)
