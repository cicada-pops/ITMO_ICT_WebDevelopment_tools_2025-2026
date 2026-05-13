# Проверка работы стенда

Скрипты ниже выполнялись на запущенном `docker compose up -d --build`.

## Состояние контейнеров

```
$ docker compose ps
NAME            STATUS                    PORTS
lr_3-app-1      Up 13 seconds             0.0.0.0:8030->8000/tcp
lr_3-db-1       Up (healthy)              0.0.0.0:5434->5432/tcp
lr_3-parser-1   Up                        0.0.0.0:8031->8001/tcp
lr_3-redis-1    Up (healthy)              0.0.0.0:6390->6379/tcp
lr_3-worker-1   Up
```

## Health-checks

```
$ curl http://localhost:8030/health
{"status":"ok"}

$ curl http://localhost:8031/health
{"status":"ok"}
```

## Синхронный парсинг через `app`

```
$ curl -X POST http://localhost:8030/parse \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://example.com/"}'
{"url":"https://example.com/","title":"Example Domain","id":1}

$ curl -X POST http://localhost:8030/parse \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://www.python.org/"}'
{"url":"https://www.python.org/","title":"Welcome to Python.org","id":2}
```

## Асинхронный парсинг через Celery

```
$ curl -X POST http://localhost:8030/parse/async \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
{"task_id":"f32eb337-bc29-4315-a6b3-8a8d5470dc15","status":"queued"}

$ sleep 2 && curl http://localhost:8030/parse/status/f32eb337-bc29-4315-a6b3-8a8d5470dc15
{
  "task_id": "f32eb337-bc29-4315-a6b3-8a8d5470dc15",
  "status": "SUCCESS",
  "result": {
    "id": 3,
    "url": "https://docs.python.org/3/library/asyncio.html",
    "title": "asyncio — Asynchronous I/O — Python 3.14.5 documentation"
  }
}
```

Время от постановки задачи до перехода в `SUCCESS` — ~0.35 с по логам
воркера.

## Чтение результатов из БД

```
$ curl http://localhost:8030/parse | python3 -m json.tool
[
    {
        "url": "https://docs.python.org/3/library/asyncio.html",
        "title": "asyncio — Asynchronous I/O — Python 3.14.5 documentation",
        "id": 3,
        "parsed_at": "2026-05-13T17:04:35.234247"
    },
    {
        "url": "https://www.python.org/",
        "title": "Welcome to Python.org",
        "id": 2,
        "parsed_at": "2026-05-13T17:03:24.715834"
    },
    {
        "url": "https://example.com/",
        "title": "Example Domain",
        "id": 1,
        "parsed_at": "2026-05-13T17:03:24.320925"
    }
]
```

## Доступные эндпоинты основного приложения

```
$ curl -s http://localhost:8030/openapi.json | python3 -c \
       "import json,sys;d=json.load(sys.stdin); \
        print(sorted(p for p in d['paths'] if '/parse' in p))"
['/parse', '/parse/async', '/parse/status/{task_id}']
```

Плюс из ЛР1: `/auth/...`, `/users/...`, `/hackathons/...`,
`/teams/...`, `/participants/...`, `/locations/...`, `/tasks/...`.

## Swagger

- основной API: <http://localhost:8030/docs>
- парсер: <http://localhost:8031/docs>
