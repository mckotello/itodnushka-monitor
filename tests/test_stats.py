from datetime import datetime, timedelta, timezone

import pytest

from app.services.stats_service import PERIODS


def test_available_periods():
    assert set(PERIODS) == {"1h", "24h", "7d", "30d"}


def test_period_values():
    assert PERIODS["1h"] == timedelta(hours=1)
    assert PERIODS["24h"] == timedelta(hours=24)
    assert PERIODS["7d"] == timedelta(days=7)
    assert PERIODS["30d"] == timedelta(days=30)


def test_period_calculation():
    ended_at = datetime.now(timezone.utc)
    started_at = ended_at - PERIODS["24h"]

    difference = ended_at - started_at

    assert difference == timedelta(hours=24)


def test_invalid_period():
    with pytest.raises(KeyError):
        PERIODS["invalid"]