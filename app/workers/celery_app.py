from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "itodnushka_monitor",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "check-active-monitors": {
            "task": "app.workers.tasks.check_all_monitors",
            "schedule": settings.check_interval_seconds,
        },
        "cleanup-old-check-results": {
            "task": "app.workers.tasks.cleanup_old_check_results",
            "schedule": 86400,
        },
    },
)