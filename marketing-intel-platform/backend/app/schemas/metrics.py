from __future__ import annotations

from pydantic import BaseModel


class KPI(BaseModel):
    spend_usd: float
    gmv: float
    roas: float | None
    orders: float
    ctr: float | None
    cpa: float | None
    cpc: float | None


class KPICompareResponse(BaseModel):
    current: KPI
    previous: KPI
    diff_pct: dict[str, float | None]

