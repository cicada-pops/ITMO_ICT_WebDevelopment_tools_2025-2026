"""Точка входа приложения Hackathons API (Lr_3)."""
from fastapi import FastAPI

from app.connection import init_db
from app.routers import (
    auth,
    hackathons,
    locations,
    participants,
    parser,
    tasks,
    teams,
    users,
)

app = FastAPI(
    title="Hackathons API (Lr_3)",
    description=(
        "Лаб. 3: то же приложение, что в ЛР1, упакованное в Docker, плюс "
        "интеграция с сервисом парсера (синхронный вызов и очередь Celery)."
    ),
    version="3.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(hackathons.router)
app.include_router(participants.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(parser.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
