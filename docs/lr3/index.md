# Лабораторная работа №3
# Docker, парсер и очереди задач

## Студент
**Милютин Никита Александрович**  
Группа: **K3339**

---

## Тема работы

Упаковка backend-приложения для буккросинга в Docker, запуск PostgreSQL в
контейнере, интеграция отдельного сервиса парсинга через HTTP и выполнение
парсинга через очередь Redis + Celery.

---

## Цель работы

Настроить контейнерную инфраструктуру для приложения из лабораторной работы №1,
подключить к нему парсер из лабораторной работы №2 и реализовать фоновую
обработку задач через Celery.

---

## Используемый стек

- **Python**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Docker**
- **Docker Compose**
- **aiohttp**
- **BeautifulSoup**
- **httpx**
- **Redis**
- **Celery**

---

## Архитектура решения

Проект состоит из пяти контейнеров:

- **api** — основное FastAPI-приложение Bookcrossing API;
- **db** — база данных PostgreSQL;
- **parser** — отдельный FastAPI-сервис для парсинга HTML-страниц;
- **redis** — брокер сообщений и backend для результатов Celery;
- **worker** — Celery worker, выполняющий задачи парсинга в фоне.

Основное приложение получает запрос от клиента, отправляет URL в контейнер
`parser`, получает заголовок страницы и сохраняет результат в таблицу `books`.
Для длительных операций также доступен асинхронный сценарий: API ставит задачу
в Redis, а worker выполняет парсинг и запись в базу данных.

---

## Структура проекта

```text
LR3/
├── docker-compose.yml
├── README_LR3.md
├── LR1/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   └── src/
│       ├── main.py
│       ├── database.py
│       ├── celery_app.py
│       ├── routers/
│       │   └── parser.py
│       ├── tasks/
│       │   └── parser.py
│       └── schemas/
│           └── parser.py
├── LR2/
│   └── task2/
│       └── async_parser.py
└── parser_service/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

---

## Docker Compose

Для запуска всех компонентов используется файл `docker-compose.yml`.

```yaml
services:
  db:
    image: postgres:16

  parser:
    build:
      context: ./parser_service

  redis:
    image: redis:7

  api:
    build:
      context: ./LR1
    depends_on:
      db:
        condition: service_healthy
      parser:
        condition: service_started

  worker:
    build:
      context: ./LR1
    command: celery -A src.celery_app.celery_app worker --loglevel=info
```

База данных доступна внутри сети Docker по имени `db`, а сервис парсинга — по
имени `parser`. Redis доступен по имени `redis`.

---

## Ответственность сервисов

Каждый контейнер выполняет отдельную роль:

- `api` принимает HTTP-запросы пользователя, валидирует данные и возвращает
  ответы клиенту;
- `db` хранит пользователей, книги и заявки на обмен;
- `parser` загружает HTML-страницы и извлекает заголовок страницы;
- `redis` хранит очередь задач Celery и результаты выполнения задач;
- `worker` забирает задачи из Redis, вызывает `parser` и записывает результат в
  PostgreSQL.

Синхронный сценарий работает так:

```text
client -> api -> parser -> api -> db
```

Асинхронный сценарий через очередь работает так:

```text
client -> api -> redis -> worker -> parser -> worker -> db -> redis
```

После постановки задачи API не ждет окончания парсинга. Клиент получает
`task_id` и затем проверяет статус отдельным запросом.

---

## Контейнеризация основного приложения

Для FastAPI-приложения был создан `Dockerfile`. Он устанавливает зависимости,
копирует исходный код, применяет миграции Alembic и запускает сервер Uvicorn.

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

Подключение к базе данных вынесено в переменную окружения `DATABASE_URL`, чтобы
приложение могло работать как локально, так и внутри Docker Compose.

---

## Сервис парсинга

Парсер реализован как отдельное FastAPI-приложение. Он принимает URL, загружает
HTML-страницу через `aiohttp`, извлекает содержимое тега `<title>` с помощью
`BeautifulSoup` и возвращает результат в JSON.

Основной endpoint сервиса:

```text
POST /parse
```

Пример ответа:

```json
{
  "url": "https://example.com/",
  "title": "Example Domain"
}
```

---

## Интеграция с основным API

В основное приложение добавлен синхронный endpoint:

```text
POST /parser/import-book
```

Он принимает URL и `owner_id`, вызывает сервис `parser`, получает заголовок
страницы и создает запись в таблице `books`. В качестве автора используется
домен сайта, а в описание добавляется ссылка на исходную страницу.

---

## Очередь Redis и Celery

Для фоновой обработки добавлена Celery-задача `parser.import_book`. API
передает в задачу URL и `owner_id`, после чего сразу возвращает клиенту
идентификатор задачи. Worker получает задачу из Redis, вызывает сервис парсинга
и сохраняет книгу в PostgreSQL.

Основные endpoints:

```text
POST /parser/import-book-async
GET /parser/tasks/{task_id}
```

Первый endpoint ставит задачу в очередь, второй позволяет проверить статус и
получить результат выполнения.

---

## Запуск проекта

Запуск выполняется из директории `LR3`:

```bash
docker compose up --build
```

После запуска доступны:

- API: `http://localhost:8000`
- Swagger-документация: `http://localhost:8000/docs`
- Parser service: `http://localhost:8001`
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6379`

Порт PostgreSQL проброшен на `5433`, чтобы не конфликтовать с локальной базой на
стандартном порту `5432`.

---

## Проверка работы

Создание пользователя:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"lr3-user@example.com","username":"lr3user","password":"password1"}'
```

Импорт страницы как книги:

```bash
curl -X POST http://localhost:8000/parser/import-book \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","owner_id":1}'
```

Результат выполнения:

```json
{
  "url": "https://example.com/",
  "parsed_title": "Example Domain",
  "book": {
    "id": 1,
    "owner_id": 1,
    "title": "Example Domain",
    "author": "example.com",
    "description": "Imported from https://example.com/"
  }
}
```

---

## Проверка очереди

Перед проверкой нужно убедиться, что запущены все контейнеры:

```bash
docker compose ps
```

В списке должны быть сервисы `api`, `db`, `parser`, `redis` и `worker`.

Проверка Redis:

```bash
docker compose exec redis redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

Проверка Celery worker:

```bash
docker compose logs worker
```

В логах должно быть видно подключение к Redis и зарегистрированную задачу:

```text
Connected to redis://redis:6379/0
[tasks]
  . parser.import_book
```

Постановка задачи в очередь:

```bash
curl -X POST http://localhost:8000/parser/import-book-async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","owner_id":1}'
```

Пример ответа:

```json
{
  "task_id": "2ec8a1fd-8b41-4f4a-8d4f-3a0b8a2a7a54",
  "status": "queued",
  "message": "Задача парсинга добавлена в очередь."
}
```

Проверка результата:

```bash
curl http://localhost:8000/parser/tasks/2ec8a1fd-8b41-4f4a-8d4f-3a0b8a2a7a54
```

После выполнения задачи статус становится `SUCCESS`, а поле `result` содержит
данные созданной книги.

Также можно проверить, что книга действительно появилась в базе через API:

```bash
curl http://localhost:8000/books/
```

В ответе должна быть запись с названием страницы, например `Example Domain`.

---

## Вывод

В ходе работы приложение FastAPI было упаковано в Docker и объединено с
PostgreSQL, Redis, Celery worker и отдельным сервисом парсинга через Docker
Compose. Был реализован HTTP-вызов парсера из основного API, а также фоновый
запуск парсинга через очередь с сохранением результата в базу данных.
