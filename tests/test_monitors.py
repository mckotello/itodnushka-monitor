import pytest

from app.models.monitor import CheckResult, Monitor


def test_monitor_model():
    monitor = Monitor(
        name="Test site",
        url="https://example.com",
    )

    assert monitor.name == "Test site"
    assert monitor.url == "https://example.com"
    assert monitor.is_active is None


def test_check_result_model():
    result = CheckResult(
        monitor_id=1,
        status="up",
        status_code=200,
        response_time_ms=120,
    )

    assert result.monitor_id == 1
    assert result.status == "up"
    assert result.status_code == 200
    assert result.response_time_ms == 120


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, "up"),
        (201, "up"),
        (301, "up"),
        (399, "up"),
        (400, "down"),
        (404, "down"),
        (500, "down"),
    ],
)
def test_http_status_logic(status_code, expected):
    actual = "up" if 200 <= status_code < 400 else "down"

    assert actual == expected