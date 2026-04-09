"""Точка входа приложения Hackathons API."""
from fastapi import FastAPI

from app.connection import init_db
from app.routers import (
    auth,
    hackathons,
    locations,
    participants,
    tasks,
    teams,
    users,
)

app = FastAPI(
    title="Hackathons API",
    description="Система для проведения хакатонов — лабораторная работа №1.",
    version="1.0.0",
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
