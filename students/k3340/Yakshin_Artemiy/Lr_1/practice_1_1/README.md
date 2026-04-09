# Practice 1.1 — FastAPI + Pydantic (временная БД)

Тема: **Система проведения хакатонов**.

## Что реализовано

- Главная сущность `Hackathon` с одиночным вложенным объектом `Location`
  и списком вложенных объектов `Task`.
- Pydantic-модели в `models.py` с аннотацией типов.
- Полный CRUD для `Hackathon`.
- Отдельный CRUD для вложенной сущности `Task`.
- GET/PUT для одиночного вложенного объекта `Location`.
- Временная БД (`temp_bd`) с тремя записями.

## Запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Документация: <http://127.0.0.1:8000/docs>

## Эндпоинты

| Метод  | Путь | Назначение |
|--------|------|------------|
| GET    | `/hackathons` | список хакатонов |
| GET    | `/hackathon/{id}` | получить хакатон |
| POST   | `/hackathon` | создать хакатон |
| PUT    | `/hackathon/{id}` | обновить хакатон |
| DELETE | `/hackathon/{id}` | удалить хакатон |
| GET    | `/hackathon/{id}/tasks` | список задач хакатона |
| GET    | `/hackathon/{id}/task/{task_id}` | получить задачу |
| POST   | `/hackathon/{id}/task` | создать задачу |
| PUT    | `/hackathon/{id}/task/{task_id}` | обновить задачу |
| DELETE | `/hackathon/{id}/task/{task_id}` | удалить задачу |
| GET    | `/hackathon/{id}/location` | получить локацию |
| PUT    | `/hackathon/{id}/location` | обновить локацию |
