from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    last_response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    checks: Mapped[list["CheckResult"]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(primary_key=True)

    monitor_id: Mapped[int] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"),
        index=True,
    )

    status: Mapped[str] = mapped_column(String(20))
    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    monitor: Mapped["Monitor"] = relationship(
        back_populates="checks",
    )