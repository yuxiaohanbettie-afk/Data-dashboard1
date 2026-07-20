from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AdFactDaily
from app.schemas.metrics import KPI, KPICompareResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _pct(cur: float | None, prev: float | None) -> float | None:
    if cur is None or prev is None:
        return None
    if prev == 0:
        return None
    return (cur - prev) / prev


def _kpi_from_row(row) -> KPI:
    spend = float(row.spend_usd or 0.0)
    gmv = float(row.gmv or 0.0)
    clicks = float(row.clicks or 0.0)
    imps = float(row.imps or 0.0)
    orders = float(row.orders or 0.0)

    roas = (gmv / spend) if spend > 0 else None
    ctr = (clicks / imps) if imps > 0 else None
    cpc = (spend / clicks) if clicks > 0 else None
    cpa = (spend / orders) if orders > 0 else None

    return KPI(
        spend_usd=spend,
        gmv=gmv,
        roas=roas,
        orders=orders,
        ctr=ctr,
        cpa=cpa,
        cpc=cpc,
    )


def _agg(
    db: Session,
    start: date,
    end: date,
    platform: str | None,
    country: str | None,
    ad_type: str | None,
    campaign_goal: str | None,
    business_unit: str | None,
):
    q = select(
        func.sum(AdFactDaily.cost_usd).label("spend_usd"),
        func.sum(AdFactDaily.gmv).label("gmv"),
        func.sum(AdFactDaily.click).label("clicks"),
        func.sum(AdFactDaily.impression).label("imps"),
        func.sum(AdFactDaily.parent_orders).label("orders"),
    ).where(AdFactDaily.dt >= start, AdFactDaily.dt <= end)

    if platform:
        q = q.where(AdFactDaily.platform == platform.lower())
    if country:
        q = q.where(AdFactDaily.site_code == country)
    if ad_type:
        q = q.where(AdFactDaily.ad_type == ad_type)
    if campaign_goal:
        q = q.where(AdFactDaily.campaign_goal == campaign_goal)
    if business_unit:
        q = q.where(AdFactDaily.business_unit == business_unit)

    return db.execute(q).first()


@router.get("/kpi_compare", response_model=KPICompareResponse)
def kpi_compare(
    current_start: date = Query(...),
    current_end: date = Query(...),
    previous_start: date = Query(...),
    previous_end: date = Query(...),
    platform: Literal["google", "meta"] | None = Query(None),
    country: str | None = Query(None, description="site_code, e.g. NL/DE/UK"),
    ad_type: str | None = Query(None),
    campaign_goal: str | None = Query(None),
    business_unit: str | None = Query(None),
    db: Session = Depends(get_db),
):
    cur_row = _agg(db, current_start, current_end, platform, country, ad_type, campaign_goal, business_unit)
    prev_row = _agg(db, previous_start, previous_end, platform, country, ad_type, campaign_goal, business_unit)

    current = _kpi_from_row(cur_row)
    previous = _kpi_from_row(prev_row)

    diff_pct = {
        "spend_usd": _pct(current.spend_usd, previous.spend_usd),
        "gmv": _pct(current.gmv, previous.gmv),
        "roas": _pct(current.roas, previous.roas),
        "orders": _pct(current.orders, previous.orders),
        "ctr": _pct(current.ctr, previous.ctr),
        "cpa": _pct(current.cpa, previous.cpa),
        "cpc": _pct(current.cpc, previous.cpc),
    }
    return KPICompareResponse(current=current, previous=previous, diff_pct=diff_pct)

