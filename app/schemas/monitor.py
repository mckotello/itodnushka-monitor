from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    url: HttpUrl


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    url: HttpUrl | None = None
    is_active: bool | None = None


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    is_active: bool

    last_status: str | None
    last_status_code: int | None
    last_response_time_ms: int | None
    last_checked_at: datetime | None

    created_at: datetime
    updated_at: datetime


class CheckResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    status: str
    status_code: int | None
    response_time_ms: int | None
    error_message: str | None
    checked_at: datetime