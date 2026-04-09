# Practice 1.2 — SQLModel + PostgreSQL

Тема: **Система проведения хакатонов**.

## Модель данных

6 таблиц, связи `one-to-many` и `many-to-many` с ассоциативными сущностями:

- `Location` — 1—M — `Hackathon`
- `Hackathon` — 1—M — `Team`
- `Hackathon` — 1—M — `Task`
- `Team` — M—M — `Participant` (через `TeamParticipantLink`, поле `role`)
- `Team` — M—M — `Task` (через `Submission`, поля `repo_url`, `score`)

## Предварительная настройка

1. Установить PostgreSQL и создать БД:
   ```sql
   CREATE DATABASE hackathons_db;
   ```
2. Проверить строку подключения в `connection.py`
   (`postgresql://postgres:123@localhost/hackathons_db`).

## Запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Документация Swagger: <http://127.0.0.1:8000/docs>

## Ключевые эндпоинты

- CRUD для `Location`, `Hackathon`, `Team`, `Participant`, `Task`.
- `GET /hackathon/{id}` — возвращает хакатон с вложенной локацией, списком
  команд и списком задач (one-to-many).
- `GET /team/{id}` — возвращает команду с вложенными участниками и задачами
  (many-to-many).
- `POST /team/{team_id}/add_participant/{participant_id}?role=developer` —
  создание записи в ассоциативной таблице.
- `POST /team/{team_id}/submit/{task_id}?repo_url=...&score=...` —
  создание сдачи (вторая ассоциативная таблица).
