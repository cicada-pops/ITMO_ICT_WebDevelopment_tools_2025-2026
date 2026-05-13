# Подзадача 1. Упаковка в Docker

## Dockerfile основного приложения — `main_app/Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Сначала ставятся зависимости (отдельный слой кешируется при повторных
сборках), потом копируется код — стандартная двухслойная схема.

## Dockerfile парсера — `parser_app/Dockerfile`

Аналогичен, только порт 8001 и свой `requirements.txt` со списком
`fastapi[all], sqlmodel, psycopg2-binary, requests, beautifulsoup4`.

## Dockerfile воркера — `worker/Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./worker

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--queues=parse"]
```

Код кладётся не в корень, а в подкаталог `worker/`, чтобы Celery видел
пакет `worker` с обычным `__init__.py` — это позволяет регистрировать
задачи как `worker.tasks.parse_url` (имя должно совпадать у клиента и
у воркера).

## docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: hackathons_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5434:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d hackathons_db"]
      interval: 3s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6390:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 3s
      retries: 10

  parser:
    build: ./parser_app
    environment:
      DB_ADMIN: postgresql://postgres:postgres@db:5432/hackathons_db
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8031:8001"

  app:
    build: ./main_app
    environment:
      DB_ADMIN: postgresql://postgres:postgres@db:5432/hackathons_db
      JWT_SECRET: change-me-in-production
      JWT_ALGORITHM: HS256
      JWT_EXPIRES_MINUTES: 60
      PARSER_URL: http://parser:8001
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
      parser: { condition: service_started }
    ports:
      - "8030:8000"

  worker:
    build: ./worker
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      PARSER_URL: http://parser:8001
    depends_on:
      redis: { condition: service_healthy }
      parser: { condition: service_started }

volumes:
  pgdata:
```

### Ключевые моменты

- **`depends_on` + `healthcheck`**: `app` не стартует, пока `db` и
  `redis` не сообщат, что готовы. Без этого FastAPI мог бы получить
  отказ на `init_db()` при первом запуске.
- **Сетевое взаимодействие**: compose автоматически создаёт сеть
  `lr_3_default`, имена сервисов работают как DNS-имена. Поэтому
  `PARSER_URL=http://parser:8001`, а не `localhost:8001`.
- **Порты хоста сдвинуты** (5434, 6390, 8030, 8031) — на машине
  параллельно запущены другие стэки, занимающие 5432/5433, 6379/6380,
  8000.
- **Volume `pgdata`**: данные PostgreSQL переживают `docker compose
  restart`. `docker compose down -v` удалит том явно.

## Сборка и запуск

```bash
cd Lr_3
docker compose up -d --build
```

Проверка состояния:

```bash
$ docker compose ps
NAME            STATUS                    PORTS
lr_3-app-1      Up                        0.0.0.0:8030->8000/tcp
lr_3-db-1       Up (healthy)              0.0.0.0:5434->5432/tcp
lr_3-parser-1   Up                        0.0.0.0:8031->8001/tcp
lr_3-redis-1    Up (healthy)              0.0.0.0:6390->6379/tcp
lr_3-worker-1   Up
```
