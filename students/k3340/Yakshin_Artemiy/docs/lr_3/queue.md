# Подзадача 3. Очередь Celery + Redis

## Зачем

Синхронный `/parse` блокирует HTTP-воркер, пока сервис не скачает
страницу и не запишет результат в БД. Если страница тяжёлая или
парсингов много, лучше отдать клиенту `task_id` сразу и считать в
фоне. Это даёт:

- быстрый ответ API даже при долгих задачах;
- ретраи и параллельный пул воркеров «бесплатно» из коробки Celery;
- горизонтальное масштабирование: можно поднять N воркеров на одной
  очереди.

## Архитектура

```
[client] ──POST /parse/async──▶ [app] ──send_task──▶ [redis (broker)] ──▶ [worker]
                                                                              │
                                                                              ▼
                                                                          [parser]
                                                                              │
                                                                              ▼
                                                                            [db]

[client] ──GET /parse/status/{id}──▶ [app] ──AsyncResult──▶ [redis (backend)]
```

Redis выступает одновременно брокером (db 0) и backend'ом для
результатов (db 1).

## Celery-приложение воркера

`worker/celery_app.py`:

```python
from celery import Celery

celery_app = Celery(
    "lr3",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    include=["worker.tasks"],
)
celery_app.conf.task_default_queue = "parse"
celery_app.conf.result_expires = 3600
```

`worker/tasks.py`:

```python
@celery_app.task(name="worker.tasks.parse_url", bind=True, max_retries=2)
def parse_url(self, url: str) -> dict:
    try:
        resp = requests.post(
            f"{PARSER_URL}/parse",
            json={"url": url},
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=5)
    return resp.json()
```

Сама логика парсинга остаётся в сервисе `parser` — воркер только
оборачивает HTTP-вызов асинхронным API и добавляет автоматический
ретрай.

## Сторона клиента в FastAPI

`main_app/app/celery_app.py` — лёгкий клиент Celery:

```python
celery_app = Celery(
    "lr3",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.task_default_queue = "parse"
PARSE_TASK_NAME = "worker.tasks.parse_url"
```

!!! warning "Очередь должна совпадать"
    Если в `app` не выставить `task_default_queue = "parse"`, задачи
    попадут в дефолтную очередь `celery`, а воркер слушает только
    `parse`. Задачи будут вечно в статусе `PENDING`. Это самая частая
    ошибка интеграции; именно её пришлось править во время сборки
    стенда.

Эндпоинты `/parse/async` и `/parse/status/{task_id}`:

```python
@router.post("/async", response_model=ParseAsyncResponse)
def parse_async(req: ParseRequest) -> ParseAsyncResponse:
    task = celery_app.send_task(PARSE_TASK_NAME, args=[str(req.url)])
    return ParseAsyncResponse(task_id=task.id)


@router.get("/status/{task_id}", response_model=ParseStatusResponse)
def parse_status(task_id: str) -> ParseStatusResponse:
    res = AsyncResult(task_id, app=celery_app)
    payload = None
    if res.successful():
        payload = res.result if isinstance(res.result, dict) else {"value": res.result}
    elif res.failed():
        payload = {"error": str(res.result)}
    return ParseStatusResponse(task_id=task_id, status=res.status, result=payload)
```

## docker-compose: сервис worker

```yaml
worker:
  build: ./worker
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
    CELERY_RESULT_BACKEND: redis://redis:6379/1
    PARSER_URL: http://parser:8001
  depends_on:
    redis: { condition: service_healthy }
    parser: { condition: service_started }
```

Воркер сам не открывает портов наружу — он подключается к Redis за
задачами и к `parser` за работой.

## Пример асинхронного вызова

```bash
$ TASK=$(curl -s -X POST http://localhost:8030/parse/async \
         -H 'Content-Type: application/json' \
         -d '{"url":"https://docs.python.org/3/library/asyncio.html"}' \
         | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")

$ echo $TASK
f32eb337-bc29-4315-a6b3-8a8d5470dc15

$ sleep 2 && curl http://localhost:8030/parse/status/$TASK
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

Лог воркера:

```
worker-1  | [..: INFO/ForkPoolWorker-8] Task worker.tasks.parse_url[f32e...]
           |    succeeded in 0.347s: {'id': 3, 'url': '...', 'title': '...'}
```
