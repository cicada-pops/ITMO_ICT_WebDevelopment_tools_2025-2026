from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.connection import get_session
from app.models.task import Task, TaskDefault, TaskRead, TaskReadWithTeams
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskRead])
def list_tasks(session: Session = Depends(get_session)) -> List[Task]:
    return session.exec(select(Task)).all()


@router.get("/{task_id}", response_model=TaskReadWithTeams)
def get_task(task_id: int, session: Session = Depends(get_session)) -> Task:
    """Возвращает задачу с вложенным списком команд (m2m через Submission)."""
    t = session.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@router.post("", response_model=TaskRead)
def create_task(
    data: TaskDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Task:
    t = Task.model_validate(data)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    data: TaskDefault,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Task:
    t = session.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    t = session.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(t)
    session.commit()
    return {"ok": True}
