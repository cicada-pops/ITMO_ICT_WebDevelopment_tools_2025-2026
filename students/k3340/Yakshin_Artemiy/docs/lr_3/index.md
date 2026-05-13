# Лабораторная работа №3 — Docker, парсер, очередь Celery

## Цель

Упаковать FastAPI-приложение в Docker, реализовать отдельный
сервис-парсер, вызвать его из основного API синхронно (HTTP) и
асинхронно (через очередь Celery + Redis).

## Состав стека

5 сервисов в `docker-compose.yml`:

| Сервис | Образ / контекст       | Назначение |
|--------|------------------------|------------|
| `db`     | `postgres:16-alpine`   | БД из ЛР1 (`hackathons_db`) + новая таблица `parsed_page` |
| `redis`  | `redis:7-alpine`       | Брокер и backend для Celery |
| `parser` | `parser_app/Dockerfile`| Самостоятельный FastAPI: `/parse`, фактический загрузчик страниц |
| `app`    | `main_app/Dockerfile`  | FastAPI из ЛР1 + новые ручки `/parse`, `/parse/async` |
| `worker` | `worker/Dockerfile`    | Celery-воркер, читает задачи из Redis, дёргает `parser` |

```
client ──HTTP──▶ app ──┬──HTTP (sync)──▶ parser ──▶ db
                       │
                       └──enqueue──▶ redis ──▶ worker ──HTTP──▶ parser ──▶ db
                                                ▲
                                                │
                       client ◀─poll status─────┘ via /parse/status/{task_id}
```

## Разделы отчёта

| # | Этап | Страница |
|---|------|----------|
| 1 | Упаковка в Docker (Dockerfile, compose) | [docker](docker.md) |
| 2 | Сервис-парсер и синхронный вызов из API | [parser](parser.md) |
| 3 | Очередь Celery + Redis, асинхронный вызов | [queue](queue.md) |
| — | Проверка работы (smoke) | [verify](verify.md) |

## Ссылки на исходный код

- [`Lr_3/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_3/) — корень
- [`Lr_3/docker-compose.yml`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/HEAD/students/k3340/Yakshin_Artemiy/Lr_3/docker-compose.yml)
- [`Lr_3/main_app/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_3/main_app/)
- [`Lr_3/parser_app/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_3/parser_app/)
- [`Lr_3/worker/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_3/worker/)
