from datetime import datetime

from pydantic import BaseModel


class MonitorStatsResponse(BaseModel):
    monitor_id: int
    period: str

    total_checks: int
    successful_checks: int
    failed_checks: int

    uptime_percent: float

    average_response_time_ms: float | None
    min_response_time_ms: int | None
    max_response_time_ms: int | None

    period_started_at: datetime
    period_ended_at: datetime