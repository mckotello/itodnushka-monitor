# ITоднушка Monitor

Сервис мониторинга доступности сайтов и API.

ITоднушка Monitor регулярно проверяет указанные URL, сохраняет историю проверок, рассчитывает uptime и время ответа, а также отправляет уведомления в Telegram при изменении состояния сервиса.

## Возможности

* добавление и удаление мониторов;
* включение и отключение мониторинга;
* ручная проверка URL;
* автоматические проверки по расписанию;
* определение статуса `up` / `down`;
* сохранение истории проверок;
* статистика за `1h`, `24h`, `7d`, `30d`;
* расчёт uptime;
* среднее, минимальное и максимальное время ответа;
* Telegram-уведомления при падении и восстановлении;
* веб-дашборд;
* REST API;
* PostgreSQL;
* Redis;
* Celery и Celery Beat;
* миграции через Alembic;
* Docker Compose;
* автоматические тесты;
* CI через GitHub Actions.

## Стек

### Backend

* Python 3.13
* FastAPI
* SQLAlchemy 2
* Pydantic
* httpx
* PostgreSQL
* asyncpg

### Background jobs

* Celery
* Redis
* Celery Beat

### Infrastructure

* Docker
* Docker Compose
* Alembic

### Frontend

* HTML
* CSS
* JavaScript
* Canvas API

### Testing

* pytest
* pytest-asyncio

### CI

* GitHub Actions

## Архитектура

```text
                         ┌─────────────────┐
                         │     Browser     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         │       API       │
                         └───────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              PostgreSQL       Redis      HTTP checks
                    ▲            ▲            │
                    │            │            ▼
                    │       ┌────┴─────┐   Monitors
                    │       │  Celery  │
                    │       │  Worker  │
                    │       └────▲─────┘
                    │            │
                    │       ┌────┴─────┐
                    │       │  Celery  │
                    │       │   Beat   │
                    │       └──────────┘
                    │
                    └──────────────────────┐
                                           │
                                           ▼
                                  Telegram notifications
```

## Структура проекта

```text
itodnushka-monitor/
│
├── app/
│   ├── api/
│   │   └── monitors.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── monitor.py
│   │
│   ├── schemas/
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
│   │   └── 0001_create_monitors.py
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── test_monitors.py
│   └── test_stats.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
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
git clone https://github.com/YOUR_USERNAME/itodnushka-monitor.git
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

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Telegram-параметры можно оставить пустыми. В этом случае мониторинг будет работать без уведомлений.

### 3. Запуск

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Должны работать:

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

## API

### Создать монитор

```http
POST /api/monitors
```

Пример:

```json
{
  "name": "Example",
  "url": "https://example.com"
}
```

### Получить список мониторов

```http
GET /api/monitors
```

### Получить монитор

```http
GET /api/monitors/{monitor_id}
```

### Изменить монитор

```http
PATCH /api/monitors/{monitor_id}
```

### Удалить монитор

```http
DELETE /api/monitors/{monitor_id}
```

### Выполнить проверку

```http
POST /api/monitors/{monitor_id}/check
```

### Получить историю

```http
GET /api/monitors/{monitor_id}/history
```

Количество результатов можно ограничить:

```text
GET /api/monitors/1/history?limit=50
```

### Получить статистику

```http
GET /api/monitors/{monitor_id}/stats?period=24h
```

Доступные периоды:

* `1h`
* `24h`
* `7d`
* `30d`

## Как работает мониторинг

Celery Beat запускает задачу проверки активных мониторов с интервалом, указанным в:

```env
CHECK_INTERVAL_SECONDS=60
```

Celery Worker получает список активных мониторов и выполняет HTTP-запросы.

Для каждого запроса сохраняются:

* HTTP status code;
* статус `up` / `down`;
* время ответа;
* сообщение об ошибке;
* время проверки.

Последнее состояние дополнительно сохраняется в таблице `monitors`.

## Telegram

При изменении состояния монитор может отправить уведомление.

Для включения уведомлений необходимо указать:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Уведомление отправляется при переходе:

```text
up → down
```

или:

```text
down → up
```

## Статистика

Для каждого монитора рассчитываются:

* количество проверок;
* успешные проверки;
* неуспешные проверки;
* uptime;
* среднее время ответа;
* минимальное время ответа;
* максимальное время ответа.

Пример ответа:

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

## Тесты

Запустить тесты:

```bash
docker compose exec api pytest -v
```

Текущая тестовая база проверяет:

* модели мониторинга;
* результаты проверок;
* определение `up` / `down`;
* доступные периоды статистики;
* расчёт временных интервалов;
* обработку некорректного периода.

## CI

GitHub Actions автоматически запускает тесты при:

* `push` в `main` или `master`;
* создании Pull Request.

Workflow:

```text
.github/workflows/ci.yml
```

## Миграции

Создать новую миграцию:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Применить миграции:

```bash
docker compose exec api alembic upgrade head
```

Откатить последнюю миграцию:

```bash
docker compose exec api alembic downgrade -1
```

## Остановка

```bash
docker compose down
```

Остановка с удалением данных PostgreSQL:

```bash
docker compose down -v
```

> `docker compose down -v` удаляет данные PostgreSQL.

## Что демонстрирует проект

Проект демонстрирует практическую работу с:

* Python;
* асинхронным программированием;
* FastAPI;
* REST API;
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
* тестированием;
* GitHub Actions;
* frontend без тяжёлого JavaScript-фреймворка.

## Автор

**ITоднушка**

Разработка сайтов, веб-сервисов, автоматизация и интеграции для бизнеса.
