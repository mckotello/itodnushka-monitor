from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.stats import MonitorStatsResponse
from app.services.stats_service import get_monitor_stats
from app.core.database import get_db
from app.models.monitor import CheckResult, Monitor
from app.schemas.monitor import (
    CheckResultResponse,
    MonitorCreate,
    MonitorResponse,
    MonitorUpdate,
)
from app.services.monitor_service import check_monitor


router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.post(
    "",
    response_model=MonitorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_monitor(
    data: MonitorCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Monitor).where(Monitor.url == str(data.url))
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Monitor with this URL already exists",
        )

    monitor = Monitor(
        name=data.name,
        url=str(data.url),
    )

    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)

    return monitor


@router.get(
    "",
    response_model=list[MonitorResponse],
)
async def list_monitors(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).order_by(Monitor.id.desc())
    )

    return result.scalars().all()

@router.get(
    "/{monitor_id}/stats",
    response_model=MonitorStatsResponse,
)
async def monitor_stats(
    monitor_id: int,
    period: str = "24h",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    try:
        return await get_monitor_stats(
            db,
            monitor,
            period,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
@router.get(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def get_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    return monitor


@router.patch(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def update_monitor(
    monitor_id: int,
    data: MonitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    updates = data.model_dump(exclude_unset=True)

    if "url" in updates and updates["url"] is not None:
        updates["url"] = str(updates["url"])

    for field, value in updates.items():
        setattr(monitor, field, value)

    await db.commit()
    await db.refresh(monitor)

    return monitor


@router.delete(
    "/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    await db.delete(monitor)
    await db.commit()


@router.post(
    "/{monitor_id}/check",
    response_model=CheckResultResponse,
)
async def run_check(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    return await check_monitor(db, monitor)


@router.get(
    "/{monitor_id}/history",
    response_model=list[CheckResultResponse],
)
async def monitor_history(
    monitor_id: int,
    limit: int = 100,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    monitor_result = await db.execute(
        select(Monitor).where(Monitor.id == monitor_id)
    )

    monitor = monitor_result.scalar_one_or_none()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    if status_filter is not None and status_filter not in {
        "up",
        "down",
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Available: up, down",
        )

    query = (
        select(CheckResult)
        .where(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(min(max(limit, 1), 500))
    )

    if status_filter is not None:
        query = query.where(
            CheckResult.status == status_filter,
        )

    result = await db.execute(query)

    return result.scalars().all()