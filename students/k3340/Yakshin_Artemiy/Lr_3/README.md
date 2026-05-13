# Лабораторная работа №3 — Docker, парсер, очередь Celery

## Что внутри

```
Lr_3/
├── docker-compose.yml
├── main_app/        # FastAPI из ЛР1 + роутер /parse и /parse/async
│   └── Dockerfile
├── parser_app/      # отдельный FastAPI-сервис парсера
│   └── Dockerfile
├── worker/          # Celery-воркер
│   └── Dockerfile
└── README.md
```

Стек: **postgres, redis, main_app, parser_app, worker** — пять
контейнеров, одна команда запуска.

## Запуск

```bash
cd Lr_3
docker compose up -d --build
# дождаться "healthy" у db и redis (~5 секунд)
```

Порты на хосте:

| Сервис | Порт хоста | Порт контейнера |
|---|---:|---:|
| `app` (FastAPI основной) | 8030 | 8000 |
| `parser` (FastAPI-парсер) | 8031 | 8001 |
| `db` (PostgreSQL)         | 5434 | 5432 |
| `redis`                   | 6390 | 6379 |

Порты сдвинуты, чтобы не конфликтовать с другими контейнерами на
машине. Внутри сети compose сервисы общаются по именам:
`http://parser:8001`, `db:5432`, `redis:6379`.

## Эндпоинты `app`

| Метод | Путь | Описание |
|---|---|---|
| POST | `/parse` | Синхронно проксирует в parser, возвращает `{id,url,title}` |
| POST | `/parse/async` | Кладёт задачу в Celery, возвращает `task_id` |
| GET  | `/parse/status/{task_id}` | Статус задачи Celery |
| GET  | `/parse` | Последние записи `parsed_page` |
| GET  | `/health` | Проба готовности |
| ... | `/auth`, `/hackathons`, `/teams`, ...| Эндпоинты из ЛР1 |

## Эндпоинты `parser`

| Метод | Путь | Описание |
|---|---|---|
| POST | `/parse` | Загружает страницу, извлекает `<title>`, пишет в `parsed_page` |
| GET  | `/health` | Проба готовности |

Swagger: <http://localhost:8030/docs> и <http://localhost:8031/docs>.

## Проверка работы (smoke)

```bash
# health
curl http://localhost:8030/health

# синхронно
curl -X POST http://localhost:8030/parse \
     -H 'Content-Type: application/json' \
     -d '{"url":"https://example.com/"}'
# -> {"url":"https://example.com/","title":"Example Domain","id":1}

# асинхронно через очередь
TASK=$(curl -s -X POST http://localhost:8030/parse/async \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://www.python.org/"}' \
       | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")
sleep 2
curl http://localhost:8030/parse/status/$TASK
# -> {"task_id":"...","status":"SUCCESS","result":{"id":2,"url":"...","title":"Welcome to Python.org"}}
```

## Остановка

```bash
docker compose down            # стопнуть контейнеры
docker compose down -v         # + удалить volume с данными PostgreSQL
```
