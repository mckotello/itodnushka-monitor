from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitor import CheckResult, Monitor


PERIODS = {
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


async def get_monitor_stats(
    db: AsyncSession,
    monitor: Monitor,
    period: str,
):
    if period not in PERIODS:
        raise ValueError(
            "Invalid period. Available: 1h, 24h, 7d, 30d"
        )

    period_ended_at = datetime.now(timezone.utc)
    period_started_at = period_ended_at - PERIODS[period]

    result = await db.execute(
        select(
            func.count(CheckResult.id),
            func.sum(
                (CheckResult.status == "up").cast(Integer)
            ),
            func.sum(
                (CheckResult.status == "down").cast(Integer)
            ),
            func.avg(CheckResult.response_time_ms),
            func.min(CheckResult.response_time_ms),
            func.max(CheckResult.response_time_ms),
        )
        .where(
            CheckResult.monitor_id == monitor.id,
            CheckResult.checked_at >= period_started_at,
            CheckResult.checked_at <= period_ended_at,
        )
    )

    (
        total_checks,
        successful_checks,
        failed_checks,
        average_response_time,
        min_response_time,
        max_response_time,
    ) = result.one()

    total_checks = total_checks or 0
    successful_checks = successful_checks or 0
    failed_checks = failed_checks or 0

    uptime_percent = (
        round(successful_checks / total_checks * 100, 2)
        if total_checks
        else 0.0
    )

    return {
        "monitor_id": monitor.id,
        "period": period,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percent": uptime_percent,
        "average_response_time_ms": (
            round(float(average_response_time), 2)
            if average_response_time is not None
            else None
        ),
        "min_response_time_ms": min_response_time,
        "max_response_time_ms": max_response_time,
        "period_started_at": period_started_at,
        "period_ended_at": period_ended_at,
    }