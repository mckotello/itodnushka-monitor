from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.monitor import CheckResult, Monitor
from app.workers.tasks import (
    _check_all_monitors,
    _check_one_monitor,
    _cleanup_old_check_results,
)


@pytest.mark.asyncio
async def test_check_all_monitors_checks_active_monitors(
    db_session,
    monkeypatch,
):
    checked_monitor_ids = []

    async def fake_check_monitor(db, monitor):
        checked_monitor_ids.append(monitor.id)

    monkeypatch.setattr(
        "app.workers.tasks.check_monitor",
        fake_check_monitor,
    )

    active_monitor = Monitor(
        name="Active",
        url="https://active-test.example.com",
        is_active=True,
    )

    inactive_monitor = Monitor(
        name="Inactive",
        url="https://inactive-test.example.com",
        is_active=False,
    )

    db_session.add_all(
        [
            active_monitor,
            inactive_monitor,
        ]
    )

    await db_session.commit()
    await db_session.refresh(active_monitor)
    await db_session.refresh(inactive_monitor)

    result = await _check_all_monitors(
        session_factory=lambda: db_session
    )

    assert result == 1
    assert checked_monitor_ids == [
        active_monitor.id,
    ]


@pytest.mark.asyncio
async def test_check_one_monitor_missing(
    db_session,
):
    result = await _check_one_monitor(
        999999,
        session_factory=lambda: db_session,
    )

    assert result == {
        "status": "error",
        "message": "Monitor not found",
        "monitor_id": 999999,
    }


@pytest.mark.asyncio
async def test_check_one_monitor(
    db_session,
    monkeypatch,
):
    monitor = Monitor(
        name="Test",
        url="https://one-test.example.com",
        is_active=True,
    )

    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)

    class FakeCheckResult:
        status = "up"
        status_code = 200
        response_time_ms = 123

    async def fake_check_monitor(db, monitor):
        return FakeCheckResult()

    monkeypatch.setattr(
        "app.workers.tasks.check_monitor",
        fake_check_monitor,
    )

    result = await _check_one_monitor(
        monitor.id,
        session_factory=lambda: db_session,
    )

    assert result == {
        "status": "up",
        "status_code": 200,
        "response_time_ms": 123,
        "monitor_id": monitor.id,
    }


@pytest.mark.asyncio
async def test_cleanup_old_check_results(
    db_session,
):
    monitor = Monitor(
        name="Cleanup test",
        url="https://cleanup-test.example.com",
        is_active=True,
    )

    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)

    old_result = CheckResult(
        monitor_id=monitor.id,
        status="up",
        status_code=200,
        response_time_ms=100,
        checked_at=(
            datetime.now(timezone.utc)
            - timedelta(days=31)
        ),
    )

    recent_result = CheckResult(
        monitor_id=monitor.id,
        status="up",
        status_code=200,
        response_time_ms=100,
        checked_at=datetime.now(timezone.utc),
    )

    db_session.add_all(
        [
            old_result,
            recent_result,
        ]
    )

    await db_session.commit()

    result = await _cleanup_old_check_results(
        session_factory=lambda: db_session,
    )

    assert result == 1

    remaining = await db_session.execute(
        select(CheckResult).where(
            CheckResult.monitor_id == monitor.id
        )
    )

    remaining_results = remaining.scalars().all()

    assert len(remaining_results) == 1
    assert remaining_results[0].id == recent_result.id