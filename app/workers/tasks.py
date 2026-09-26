import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.monitor import CheckResult, Monitor
from app.services.monitor_service import check_monitor
from app.workers.celery_app import celery_app


async def _check_all_monitors() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Monitor).where(
                Monitor.is_active.is_(True),
            )
        )

        monitors = result.scalars().all()

        checked_count = 0

        for monitor in monitors:
            await check_monitor(db, monitor)
            checked_count += 1

        return checked_count


@celery_app.task(
    name="app.workers.tasks.check_all_monitors",
)
def check_all_monitors() -> int:
    return asyncio.run(_check_all_monitors())


@celery_app.task(
    name="app.workers.tasks.check_one_monitor",
)
def check_one_monitor(monitor_id: int) -> dict:
    return asyncio.run(_check_one_monitor(monitor_id))


async def _check_one_monitor(monitor_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Monitor).where(Monitor.id == monitor_id)
        )

        monitor = result.scalar_one_or_none()

        if monitor is None:
            return {
                "status": "error",
                "message": "Monitor not found",
                "monitor_id": monitor_id,
            }

        check_result = await check_monitor(db, monitor)

        return {
            "status": check_result.status,
            "status_code": check_result.status_code,
            "response_time_ms": check_result.response_time_ms,
            "monitor_id": monitor_id,
        }

@celery_app.task(
    name="app.workers.tasks.cleanup_old_check_results",
)
def cleanup_old_check_results() -> int:
    return asyncio.run(_cleanup_old_check_results())

async def _cleanup_old_check_results() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=settings.check_result_retention_days,
    )

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            delete(CheckResult).where(
                CheckResult.checked_at < cutoff,
            )
        )

        await db.commit()

        return result.rowcount or 0