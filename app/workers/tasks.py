import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.monitor import Monitor
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