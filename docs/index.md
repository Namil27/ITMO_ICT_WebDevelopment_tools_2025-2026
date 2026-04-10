# Лабораторная работа №1
# Веб-приложение для буккросинга

## Студент
**Милютин Никита Александрович**  
Группа: **K3339**

---

## Тема работы

Разработка backend-части веб-приложения для буккросинга на основе **FastAPI + PostgreSQL**.

---

## Цель работы

Разработать backend-систему, которая позволяет пользователям:

- создавать профиль;
- добавлять книги в личную библиотеку;
- просматривать книги других пользователей;
- отправлять запросы на обмен;
- подтверждать или отклонять запросы;
- регистрироваться и входить в систему;
- работать с защищенными эндпоинтами через JWT.

---

## Используемый стек

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Alembic**
- **Docker / Docker Compose**
- **Pydantic**
- **JWT**
- **pwdlib**
- **python-jose**

---

## Архитектура проекта

Проект реализован по слоям:

- **models** — ORM-модели SQLAlchemy;
- **schemas** — Pydantic-схемы для запросов и ответов API;
- **crud** — функции для работы с БД;
- **routers** — FastAPI-роутеры;
- **core** — настройки и security-функции;
- **dependencies** — зависимости FastAPI, в том числе получение сессии БД и текущего пользователя.

---

## Структура проекта

```text
LR1/
├── docker-compose.yml
├── seed_api.py
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── docs/
│   └── index.md
└── src/
    ├── main.py
    ├── database.py
    ├── dependencies.py
    ├── core/
    │   ├── config.py
    │   └── security.py
    ├── crud/
    │   ├── auth.py
    │   ├── user.py
    │   ├── book.py
    │   └── exchange_request.py
    ├── dependencies/
    │   └── auth.py
    ├── models/
    │   ├── user.py
    │   ├── book.py
    │   └── exchange_request.py
    ├── routers/
    │   ├── auth.py
    │   ├── user.py
    │   ├── book.py
    │   └── exchange_request.py
    └── schemas/
        ├── auth.py
        ├── user.py
        ├── book.py
        └── exchange_request.py
```

---

## Предметная область

В системе выделены три основные сущности:

### 1. User
Пользователь системы.  
Содержит данные профиля и данные, необходимые для регистрации и аутентификации.

### 2. Book
Книга, добавленная пользователем в свою библиотеку.  
Каждая книга принадлежит конкретному пользователю и может быть доступна для обмена.

### 3. ExchangeRequest
Запрос на обмен книгой между пользователями.  
Позволяет отслеживать статус обмена: ожидание, подтверждение, отклонение или отмена.

---

## Связи между сущностями

- Один **User** может иметь много **Book**
- Один **User** может отправить много **ExchangeRequest**
- Один **User** может получить много **ExchangeRequest**
- Одна **Book** может иметь много **ExchangeRequest**

То есть:

- `User 1 -> N Book`
- `User 1 -> N ExchangeRequest` как отправитель
- `User 1 -> N ExchangeRequest` как владелец книги
- `Book 1 -> N ExchangeRequest`

---

## Модели базы данных

### Таблица `users`

Хранит информацию о пользователях.

Поля:

- `id` — первичный ключ
- `email` — уникальный email
- `username` — уникальное имя пользователя
- `hashed_password` — хэш пароля
- `full_name` — имя пользователя
- `city` — город
- `bio` — краткая информация о пользователе
- `is_active` — активен ли пользователь
- `created_at` — дата создания
- `updated_at` — дата обновления

---

### Таблица `books`

Хранит книги пользователей.

Поля:

- `id` — первичный ключ
- `owner_id` — внешний ключ на `users.id`
- `title` — название книги
- `author` — автор
- `description` — описание
- `genre` — жанр
- `condition` — состояние книги
- `exchange_status` — статус книги (`available`, `reserved`, `exchanged`)
- `is_available` — доступна ли книга для обмена
- `created_at` — дата создания
- `updated_at` — дата обновления

---

### Таблица `exchange_requests`

Хранит запросы на обмен.

Поля:

- `id` — первичный ключ
- `book_id` — внешний ключ на `books.id`
- `requester_id` — внешний ключ на `users.id`
- `owner_id` — внешний ключ на `users.id`
- `message` — сообщение к запросу
- `status` — статус запроса (`pending`, `accepted`, `rejected`, `cancelled`)
- `created_at` — дата создания
- `updated_at` — дата обновления
- `responded_at` — дата ответа

Также используется ограничение, запрещающее пользователю отправлять запрос самому себе.

---

## Подключение к базе данных

Для хранения данных используется **PostgreSQL**, поднятый в контейнере Docker.

Подключение к БД реализовано через SQLAlchemy.

Пример конфигурации подключения:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/bookcrossing_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
```

Для управления структурой базы данных использовался **Alembic**.

---

## Docker Compose

Для запуска PostgreSQL использовался `docker-compose.yml`.

Пример конфигурации:

```yaml
services:
  db:
    image: postgres:16
    container_name: bookcrossing_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: bookcrossing_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Pydantic-схемы

Для каждой сущности были реализованы схемы трех типов:

- `Create`
- `Update`
- `Read`

Также были добавлены вложенные схемы для возврата связанных данных, например:

- пользователь со списком книг;
- книга с владельцем;
- запрос на обмен с книгой и пользователями.

Это позволяет удобно формировать ответы API и отделять внутренние ORM-модели от внешнего интерфейса.

---

## CRUD-слой

Для каждой сущности были реализованы базовые операции.

### Для пользователей
- создание пользователя;
- получение пользователя по id;
- получение пользователя по email;
- получение пользователя по username;
- получение списка пользователей;
- обновление пользователя;
- удаление пользователя;
- получение пользователя вместе с книгами.

### Для книг
- создание книги;
- получение книги по id;
- получение списка книг;
- получение книг конкретного пользователя;
- получение только доступных книг;
- обновление книги;
- удаление книги;
- получение книги вместе с владельцем.

### Для запросов на обмен
- создание запроса;
- получение запроса по id;
- получение списка запросов;
- получение входящих запросов;
- получение исходящих запросов;
- обновление запроса;
- удаление запроса;
- получение полного запроса вместе с книгой и пользователями.

---

## Dependency для БД

Для FastAPI была реализована зависимость `get_db()`, которая открывает сессию базы данных перед запросом и закрывает ее после завершения обработки.

Пример:

```python
from collections.abc import Generator
from sqlalchemy.orm import Session
from src.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Реализованные эндпоинты

## Auth

### `POST /auth/register`
Регистрация нового пользователя.

### `POST /auth/login`
Вход пользователя и получение JWT access token.

### `GET /auth/me`
Получение информации о текущем авторизованном пользователе.

### `POST /auth/change-password`
Смена пароля текущего пользователя.

---

## Users

### `POST /users/`
Создание пользователя.

### `GET /users/`
Получение списка пользователей.

### `GET /users/{user_id}`
Получение пользователя по id.

### `GET /users/{user_id}/books`
Получение пользователя вместе с его книгами.

### `PATCH /users/{user_id}`
Обновление данных пользователя.

### `DELETE /users/{user_id}`
Удаление пользователя.

---

## Books

### `POST /books/`
Создание книги.

### `GET /books/`
Получение списка книг.

### `GET /books/available`
Получение только доступных для обмена книг.

### `GET /books/owner/{owner_id}`
Получение книг конкретного пользователя.

### `GET /books/{book_id}`
Получение книги по id.

### `GET /books/{book_id}/owner`
Получение книги вместе с владельцем.

### `PATCH /books/{book_id}`
Обновление книги.

### `DELETE /books/{book_id}`
Удаление книги.

---

## Exchange Requests

### `POST /exchange-requests/`
Создание запроса на обмен.

### `GET /exchange-requests/`
Получение списка запросов.

### `GET /exchange-requests/incoming/{owner_id}`
Получение входящих запросов для владельца книг.

### `GET /exchange-requests/outgoing/{requester_id}`
Получение исходящих запросов пользователя.

### `GET /exchange-requests/{request_id}`
Получение запроса по id.

### `GET /exchange-requests/{request_id}/full`
Получение запроса вместе с книгой, отправителем и владельцем.

### `PATCH /exchange-requests/{request_id}`
Обновление запроса.

### `DELETE /exchange-requests/{request_id}`
Удаление запроса.

---

## JWT-аутентификация

Для реализации функционала на 15 баллов были добавлены:

- хэширование паролей;
- проверка пароля;
- генерация JWT access token;
- получение текущего пользователя по токену;
- смена пароля.

Для хэширования использовалась библиотека **pwdlib**.  
Для JWT использовалась библиотека **python-jose**.  
Для получения токена из запроса использовался `OAuth2PasswordBearer`.

---

## Тестирование API

После запуска приложения все эндпоинты можно было проверить через Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Дополнительно был написан скрипт `seed_api.py`, который заполняет базу тестовыми данными через API:

- создает пользователей;
- добавляет книги;
- создает запросы на обмен.

Это позволило быстро проверить корректность работы всех основных эндпоинтов.

---

## Запуск проекта

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic email-validator requests python-multipart "python-jose[cryptography]" "pwdlib[argon2]"
```

### 2. Запуск базы данных

```bash
docker compose up -d
```

### 3. Применение миграций

```bash
alembic upgrade head
```

### 4. Запуск приложения

```bash
uvicorn src.main:app --reload
```

---

## Ссылка на исходный код

### Репозиторий
**[Ссылка на GitHub-репозиторий](https://github.com/Namil27/ITMO_ICT_WebDevelopment_tools_2025-2026)**


---

## Вывод

В ходе лабораторной работы был разработан backend веб-приложения для буккросинга на основе **FastAPI** и **PostgreSQL**. Была спроектирована предметная область, реализованы ORM-модели, Pydantic-схемы, CRUD-слой, роутеры и подключение к базе данных через SQLAlchemy. Для управления структурой базы данных были применены миграции Alembic, а сама база данных запускалась в Docker-контейнере.

Дополнительно был реализован функционал на 15 баллов: регистрация, логин, JWT-аутентификация, хэширование паролей, получение текущего пользователя и смена пароля. В результате получилось работающее backend-приложение с разделением на логические слои и набором REST-эндпоинтов, пригодное для дальнейшего расширения и подключения frontend-части.