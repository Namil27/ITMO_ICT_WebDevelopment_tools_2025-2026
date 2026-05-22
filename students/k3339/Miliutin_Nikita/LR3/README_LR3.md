# Лабораторная работа 3

В работе настроены контейнеры для FastAPI-приложения из LR1, PostgreSQL,
отдельного сервиса парсинга на FastAPI, Redis и Celery worker.

## Структура

- `LR1/` - основное приложение Bookcrossing API.
- `parser_service/` - отдельный HTTP-сервис парсинга страниц.
- `docker-compose.yml` - запуск PostgreSQL, API, парсера, Redis и Celery worker.

## Запуск

```bash
docker compose up --build
```

После запуска доступны:

- основное API: `http://localhost:8000`
- документация API: `http://localhost:8000/docs`
- сервис парсера: `http://localhost:8001`
- Redis: `localhost:6379`

## Проверка сценария

Сначала создайте пользователя:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"reader1","password":"password1"}'
```

Затем импортируйте страницу как книгу:

```bash
curl -X POST http://localhost:8000/parser/import-book \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","owner_id":1}'
```

API отправит URL в контейнер `parser`, получит заголовок HTML-страницы и
сохранит его в таблицу `books` как название книги.

## Проверка очереди

Поставьте задачу в Celery:

```bash
curl -X POST http://localhost:8000/parser/import-book-async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","owner_id":1}'
```

В ответе будет `task_id`. Проверьте статус:

```bash
curl http://localhost:8000/parser/tasks/<task_id>
```

При успешном выполнении статус станет `SUCCESS`, а в `result` будет созданная
книга.
