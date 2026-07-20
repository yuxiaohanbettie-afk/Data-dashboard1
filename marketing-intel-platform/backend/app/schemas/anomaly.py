from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class AnomalyOut(BaseModel):
    id: int
    detected_at: datetime
    dt: date
    level: str
    dimension: str
    metric: str
    severity: str
    current_value: float | None
    baseline_value: float | None
    delta_pct: float | None
    details_json: str | None

