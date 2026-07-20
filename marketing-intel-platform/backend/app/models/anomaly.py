from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    dt: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    level: Mapped[str] = mapped_column(String, nullable=False)  # e.g. country / campaign / ad_type
    dimension: Mapped[str] = mapped_column(String, nullable=False, index=True)  # e.g. "NL" / campaign_id

    metric: Mapped[str] = mapped_column(String, nullable=False, index=True)  # spend_usd / roas / ctr ...
    severity: Mapped[str] = mapped_column(String, nullable=False)  # red / yellow

    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # JSON string: root cause decomposition, supporting metrics, etc.
    details_json: Mapped[str | None] = mapped_column(String, nullable=True)

