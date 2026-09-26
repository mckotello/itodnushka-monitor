import time
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.monitor import CheckResult, Monitor
from app.services.telegram_service import send_telegram_message


async def check_monitor(
    db: AsyncSession,
    monitor: Monitor,
) -> CheckResult:
    previous_status = monitor.last_status

    started_at = time.perf_counter()

    status = "down"
    status_code = None
    error_message = None

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(monitor.url)

        status_code = response.status_code

        if 200 <= response.status_code < 400:
            status = "up"

    except httpx.RequestError as exc:
        error_message = str(exc)

    response_time_ms = round(
        (time.perf_counter() - started_at) * 1000
    )

    checked_at = datetime.now(timezone.utc)

    result = CheckResult(
        monitor_id=monitor.id,
        status=status,
        status_code=status_code,
        response_time_ms=response_time_ms,
        error_message=error_message,
        checked_at=checked_at,
    )

    monitor.last_status = status
    monitor.last_status_code = status_code
    monitor.last_response_time_ms = response_time_ms
    monitor.last_checked_at = checked_at

    db.add(result)

    await db.commit()
    await db.refresh(result)

    if previous_status and previous_status != status:
        if status == "down":
            message = (
                "🔴 Монитор недоступен\n\n"
                f"{monitor.name}\n"
                f"{monitor.url}\n\n"
                f"HTTP: {status_code or 'нет ответа'}\n"
                f"Ошибка: {error_message or 'неизвестная ошибка'}"
            )

            await send_telegram_message(message)

        elif status == "up":
            message = (
                "🟢 Монитор снова доступен\n\n"
                f"{monitor.name}\n"
                f"{monitor.url}\n\n"
                f"HTTP: {status_code}\n"
                f"Время ответа: {response_time_ms} мс"
            )

            await send_telegram_message(message)

    return result


async def get_monitor(
    db: AsyncSession,
    monitor_id: int,
) -> Monitor | None:
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    return result.scalar_one_or_none()