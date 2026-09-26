[![CI](https://github.com/mckotello/itodnushka-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/mckotello/itodnushka-monitor/actions/workflows/ci.yml)

# ITоднушка Monitor

Сервис мониторинга доступности сайтов и API.

ITоднушка Monitor регулярно проверяет указанные URL, сохраняет историю проверок, рассчитывает uptime и время ответа, а также отправляет уведомления в Telegram при изменении состояния сервиса.

Проект построен как production-like backend с асинхронным API, фоновой обработкой задач, PostgreSQL, Redis, JWT-аутентификацией и Docker.

## Возможности

### Мониторинг

* добавление, изменение и удаление мониторов;
* включение и отключение мониторинга;
* ручная проверка URL;
* автоматические проверки по расписанию;
* определение состояния `up` / `down`;
* сохранение истории проверок;
* измерение времени HTTP-ответа;
* сохранение HTTP status code и сообщения об ошибке.

### Статистика

* uptime за `1h`, `24h`, `7d`, `30d`;
* количество проверок;
* количество успешных и неуспешных проверок;
* среднее время ответа;
* минимальное и максимальное время ответа;
* история изменения состояния.

### Аутентификация

* регистрация пользователей;
* вход по email и паролю;
* JWT access tokens;
* получение текущего пользователя;
* защищённые API endpoints;
* изоляция мониторов между пользователями;
* один и тот же URL может использоваться разными пользователями.

### Уведомления

Telegram-уведомления отправляются при изменении состояния монитора:

```text
up → down
down → up
```

### Интерфейс

* веб-дашборд;
* список мониторов;
* текущий статус;
* время последней проверки;
* response time;
* статистика;
* график ответа;
* история проверок;
* авторизация и регистрация;
* управление аккаунтом.

## Архитектура

```text
                         ┌──────────────────┐
                         │     Browser      │
                         │    Dashboard     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API        │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │ PostgreSQL  │     │    Redis    │     │  JWT Auth   │
       └─────────────┘     └──────┬──────┘     └─────────────┘
                                  │
                         ┌────────┴────────┐
                         │                 │
                         ▼                 ▼
                  ┌─────────────┐   ┌─────────────┐
                  │   Celery    │   │ Celery Beat │
                  │   Worker    │   │  Scheduler  │
                  └──────┬──────┘   └──────┬──────┘
                         │                 │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │   HTTP checks   │
                         │  monitored URLs │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Telegram     │
                         │  notifications  │
                         └─────────────────┘
```

### Поток автоматической проверки

```text
Celery Beat
    │
    │ every CHECK_INTERVAL_SECONDS
    ▼
check_all_monitors
    │
    ▼
Celery Worker
    │
    ├── HTTP request
    │
    ├── measure response time
    │
    ├── determine up/down
    │
    ├── save CheckResult
    │
    └── update Monitor
             │
             └── state changed?
                    │
                    ▼
                 Telegram
```

## Стек

### Backend

* Python 3.13
* FastAPI
* SQLAlchemy 2
* Pydantic
* async/await
* httpx
* PyJWT
* pwdlib + Argon2

### Database

* PostgreSQL
* asyncpg
* Alembic

### Background processing

* Celery
* Celery Beat
* Redis

### Frontend

* HTML
* CSS
* JavaScript
* Canvas API

### Infrastructure

* Docker
* Docker Compose

### Testing

* pytest
* pytest-asyncio
* HTTPX ASGI transport

### CI

* GitHub Actions

## Структура проекта

```text
itodnushka-monitor/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   └── monitors.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── monitor.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── monitor.py
│   │   └── stats.py
│   │
│   ├── services/
│   │   ├── monitor_service.py
│   │   ├── stats_service.py
│   │   └── telegram_service.py
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   │   ├── 0001_create_monitors.py
│   │   ├── 0002_users_and_monitor_owner.py
│   │   └── 0003_monitor_url_per_user.py
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_monitor_service.py
│   ├── test_stats.py
│   └── test_tasks.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

## Запуск

### Требования

* Docker
* Docker Compose

Проверить установку:

```bash
docker --version
docker compose version
```

### 1. Клонирование

```bash
git clone https://github.com/mckotello/itodnushka-monitor.git
cd itodnushka-monitor
```

### 2. Настройка окружения

Создать `.env` на основе `.env.example`.

Для Windows:

```powershell
Copy-Item .env.example .env
```

Минимальная конфигурация:

```env
APP_NAME=ITоднушка Monitor
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://monitor:monitor@db:5432/monitor
REDIS_URL=redis://redis:6379/0

CHECK_INTERVAL_SECONDS=60
REQUEST_TIMEOUT_SECONDS=10
CHECK_RESULT_RETENTION_DAYS=30

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

JWT_SECRET_KEY=change-me-to-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` можно оставить пустыми. В этом случае мониторинг работает без Telegram-уведомлений.

Для production необходимо использовать собственный длинный случайный `JWT_SECRET_KEY`.

### 3. Запуск

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Используются:

* `api`
* `worker`
* `beat`
* `db`
* `redis`

### 4. Миграции

```bash
docker compose exec api alembic upgrade head
```

Проверить текущую миграцию:

```bash
docker compose exec api alembic current
```

### 5. Открыть приложение

Dashboard:

```text
http://localhost:8000/
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

## Аутентификация

API использует JWT Bearer authentication.

### Регистрация

```http
POST /api/auth/register
```

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Вход

```http
POST /api/auth/login
```

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Ответ:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Полученный токен передаётся в заголовке:

```http
Authorization: Bearer <token>
```

### Текущий пользователь

```http
GET /api/auth/me
```

Все операции с мониторами требуют авторизации.

## API

### Мониторы

```http
POST   /api/monitors
GET    /api/monitors
GET    /api/monitors/{monitor_id}
PATCH  /api/monitors/{monitor_id}
DELETE /api/monitors/{monitor_id}
```

### Ручная проверка

```http
POST /api/monitors/{monitor_id}/check
```

### История

```http
GET /api/monitors/{monitor_id}/history
```

Например:

```text
GET /api/monitors/1/history?limit=50
```

Поддерживается фильтрация:

```text
GET /api/monitors/1/history?status_filter=up
GET /api/monitors/1/history?status_filter=down
```

### Статистика

```http
GET /api/monitors/{monitor_id}/stats?period=24h
```

Доступные периоды:

```text
1h
24h
7d
30d
```

## Модель данных

Основные сущности:

```text
User
 │
 └──< Monitor
          │
          └──< CheckResult
```

### User

Хранит:

* email;
* хеш пароля;
* статус активности;
* дату регистрации.

Пароли хранятся только в виде Argon2-хешей.

### Monitor

Хранит:

* владельца;
* название;
* URL;
* активность;
* последний статус;
* последний HTTP status code;
* последнее время ответа;
* время последней проверки.

Для одного пользователя URL монитора уникален.

Разные пользователи могут создать монитор одного и того же URL.

### CheckResult

Хранит историю:

* статус;
* HTTP status code;
* время ответа;
* сообщение об ошибке;
* время проверки.

## Как работает мониторинг

Celery Beat запускает периодическую задачу:

```text
check_all_monitors
```

Интервал задаётся через:

```env
CHECK_INTERVAL_SECONDS=60
```

Celery Worker получает активные мониторы и выполняет HTTP-проверки.

Для каждого запроса:

1. выполняется HTTP GET;
2. измеряется время ответа;
3. определяется статус `up` / `down`;
4. сохраняется `CheckResult`;
5. обновляется последнее состояние `Monitor`;
6. при изменении состояния отправляется Telegram-уведомление.

Успешным считается HTTP-ответ со статусом:

```text
200–399
```

Ошибки соединения и HTTP-ответы вне этого диапазона считаются состоянием `down`.

## Очистка истории

Старые результаты проверок автоматически удаляются периодической Celery-задачей.

Период хранения задаётся:

```env
CHECK_RESULT_RETENTION_DAYS=30
```

Очистка выполняется один раз в сутки.

## Telegram

Для включения уведомлений:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

При переходе:

```text
up → down
```

отправляется уведомление о недоступности.

При переходе:

```text
down → up
```

отправляется уведомление о восстановлении.

## Статистика

Для каждого монитора рассчитываются:

* количество проверок;
* успешные проверки;
* неуспешные проверки;
* uptime;
* среднее время ответа;
* минимальное время ответа;
* максимальное время ответа.

Пример:

```json
{
  "monitor_id": 1,
  "period": "24h",
  "total_checks": 1440,
  "successful_checks": 1437,
  "failed_checks": 3,
  "uptime_percent": 99.79,
  "average_response_time_ms": 184.32,
  "min_response_time_ms": 92,
  "max_response_time_ms": 841
}
```

## Тестирование

Запустить весь набор:

```bash
docker compose exec api pytest -q
```

Тесты покрывают:

* регистрацию пользователей;
* авторизацию;
* JWT;
* обработку невалидных токенов;
* получение текущего пользователя;
* создание мониторов;
* получение мониторов;
* обновление и удаление;
* изоляцию данных между пользователями;
* одинаковые URL у разных пользователей;
* историю проверок;
* фильтрацию истории;
* статистику;
* ручные проверки;
* определение `up` / `down`;
* фоновые Celery-задачи;
* пропуск неактивных мониторов;
* очистку старых результатов.

Текущий набор:

```text
46 passed
```

## CI

GitHub Actions запускает тесты автоматически при:

* `push` в `main` или `master`;
* создании Pull Request.

Workflow:

```text
.github/workflows/ci.yml
```

Статус CI отображается в верхней части README.

## Docker

Приложение состоит из пяти контейнеров:

```text
api
worker
beat
db
redis
```

Worker и API запускаются от непривилегированного пользователя.

Celery Beat хранит persistent schedule в отдельном Docker volume.

## Миграции

Создать новую миграцию:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Применить:

```bash
docker compose exec api alembic upgrade head
```

Откатить последнюю:

```bash
docker compose exec api alembic downgrade -1
```

Текущая цепочка миграций:

```text
0001_create_monitors
        │
        ▼
0002_users_and_monitor_owner
        │
        ▼
0003_monitor_url_per_user
```

## Остановка

```bash
docker compose down
```

Остановка с удалением данных PostgreSQL:

```bash
docker compose down -v
```

> `docker compose down -v` удаляет Docker volumes, включая данные PostgreSQL.

## Инженерные решения

### Асинхронный backend

FastAPI и SQLAlchemy работают в async-режиме. HTTP-проверки выполняются через `httpx.AsyncClient`.

### Фоновые задачи

Периодические проверки вынесены из HTTP API в Celery Worker.

API не блокируется выполнением внешних HTTP-запросов.

### Изоляция пользователей

Каждый монитор принадлежит конкретному пользователю.

API проверяет владельца перед операциями:

```text
GET
PATCH
DELETE
CHECK
HISTORY
STATS
```

Это предотвращает получение или изменение чужих данных через ID монитора.

### Хранение истории

Текущее состояние хранится в `monitors`, а история — в отдельной таблице `check_results`.

Такой подход позволяет быстро получить текущий статус и одновременно строить статистику по историческим данным.

### Очистка данных

История ограничивается retention-периодом, чтобы таблица результатов не росла бесконечно.

## Что демонстрирует проект

Проект демонстрирует практическую работу с:

* Python 3.13;
* асинхронным программированием;
* FastAPI;
* REST API;
* JWT-аутентификацией;
* Argon2;
* SQLAlchemy 2;
* PostgreSQL;
* Redis;
* Celery;
* Celery Beat;
* фоновыми задачами;
* асинхронными HTTP-запросами;
* Alembic;
* Docker;
* Docker Compose;
* Telegram API;
* pytest;
* GitHub Actions;
* frontend без тяжёлого JavaScript-фреймворка.

## Автор

**ITоднушка**

Разработка сайтов, веб-сервисов, автоматизация и интеграции для бизнеса.

GitHub: https://github.com/mckotello/itodnushka-monitor
