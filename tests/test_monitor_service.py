import httpx
import pytest

from app.models.monitor import Monitor
from app.services.monitor_service import check_monitor


class MockAsyncClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        if self.error:
            raise self.error

        return self.response


def make_response(status_code: int):
    return httpx.Response(
        status_code=status_code,
        request=httpx.Request(
            "GET",
            "https://example.com",
        ),
    )


@pytest.mark.asyncio
async def test_check_monitor_up(db_session, monkeypatch):
    monitor = Monitor(
        name="Example",
        url="https://example.com",
        is_active=True,
    )

    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)

    monkeypatch.setattr(
        "app.services.monitor_service.httpx.AsyncClient",
        lambda **kwargs: MockAsyncClient(
            response=make_response(200),
        ),
    )

    result = await check_monitor(
        db_session,
        monitor,
    )

    assert result.status == "up"
    assert result.status_code == 200
    assert result.response_time_ms >= 0
    assert result.error_message is None

    assert monitor.last_status == "up"
    assert monitor.last_status_code == 200
    assert monitor.last_response_time_ms >= 0
    assert monitor.last_checked_at is not None


@pytest.mark.asyncio
async def test_check_monitor_down(db_session, monkeypatch):
    monitor = Monitor(
        name="Example",
        url="https://example.com",
        is_active=True,
    )

    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)

    monkeypatch.setattr(
        "app.services.monitor_service.httpx.AsyncClient",
        lambda **kwargs: MockAsyncClient(
            response=make_response(500),
        ),
    )

    result = await check_monitor(
        db_session,
        monitor,
    )

    assert result.status == "down"
    assert result.status_code == 500
    assert result.response_time_ms >= 0

    assert monitor.last_status == "down"
    assert monitor.last_status_code == 500


@pytest.mark.asyncio
async def test_check_monitor_request_error(
    db_session,
    monkeypatch,
):
    monitor = Monitor(
        name="Example",
        url="https://example.com",
        is_active=True,
    )

    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)

    error = httpx.ConnectError(
        "Connection failed",
    )

    monkeypatch.setattr(
        "app.services.monitor_service.httpx.AsyncClient",
        lambda **kwargs: MockAsyncClient(
            error=error,
        ),
    )

    result = await check_monitor(
        db_session,
        monitor,
    )

    assert result.status == "down"
    assert result.status_code is None
    assert result.response_time_ms >= 0
    assert result.error_message == "Connection failed"

    assert monitor.last_status == "down"
    assert monitor.last_status_code is None