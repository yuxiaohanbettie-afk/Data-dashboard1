from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AdFactDaily, Anomaly


@dataclass
class Thresholds:
    spend_spike_pct: float = 0.3
    spend_drop_pct: float = -0.3
    roas_drop_pct: float = -0.15
    gmv_drop_pct: float = -0.2


class AnomalyDetector:
    def __init__(self, thresholds: Thresholds | None = None):
        self.t = thresholds or Thresholds()

    def run_for_date(self, db: Session, dt: date) -> int:
        """
        Detect anomalies after import.
        Baseline = avg(previous 7 days), Current = dt.
        Level: country (site_code) + platform.
        """
        start = dt - timedelta(days=7)
        end = dt - timedelta(days=1)

        # Current aggregates
        cur = (
            db.execute(
                select(
                    AdFactDaily.site_code,
                    AdFactDaily.platform,
                    func.sum(AdFactDaily.cost_usd).label("spend_usd"),
                    func.sum(AdFactDaily.gmv).label("gmv"),
                    func.sum(AdFactDaily.click).label("click"),
                    func.sum(AdFactDaily.impression).label("impression"),
                    func.sum(AdFactDaily.parent_orders).label("orders"),
                ).where(AdFactDaily.dt == dt)
                .group_by(AdFactDaily.site_code, AdFactDaily.platform)
            )
            .mappings()
            .all()
        )

        # Baseline aggregates (avg per day)
        base = (
            db.execute(
                select(
                    AdFactDaily.site_code,
                    AdFactDaily.platform,
                    (func.sum(AdFactDaily.cost_usd) / 7.0).label("spend_usd"),
                    (func.sum(AdFactDaily.gmv) / 7.0).label("gmv"),
                    (func.sum(AdFactDaily.click) / 7.0).label("click"),
                    (func.sum(AdFactDaily.impression) / 7.0).label("impression"),
                    (func.sum(AdFactDaily.parent_orders) / 7.0).label("orders"),
                )
                .where(AdFactDaily.dt >= start, AdFactDaily.dt <= end)
                .group_by(AdFactDaily.site_code, AdFactDaily.platform)
            )
            .mappings()
            .all()
        )
        base_map = {(r["site_code"], r["platform"]): r for r in base}

        created = 0
        for r in cur:
            key = (r["site_code"], r["platform"])
            b = base_map.get(key)
            if not b:
                continue

            spend_cur = float(r["spend_usd"] or 0.0)
            spend_base = float(b["spend_usd"] or 0.0)
            gmv_cur = float(r["gmv"] or 0.0)
            gmv_base = float(b["gmv"] or 0.0)

            roas_cur = (gmv_cur / spend_cur) if spend_cur > 0 else None
            roas_base = (gmv_base / spend_base) if spend_base > 0 else None

            def pct(cur_v: float, base_v: float) -> float | None:
                if base_v == 0:
                    return None
                return (cur_v - base_v) / base_v

            spend_delta = pct(spend_cur, spend_base)
            gmv_delta = pct(gmv_cur, gmv_base)
            roas_delta = pct(roas_cur, roas_base) if (roas_cur is not None and roas_base is not None) else None

            dimension = f"{key[0]}|{key[1]}"

            def add(metric: str, cur_v, base_v, delta, severity: str, details: dict):
                nonlocal created
                a = Anomaly(
                    dt=dt,
                    level="country",
                    dimension=dimension,
                    metric=metric,
                    severity=severity,
                    current_value=cur_v,
                    baseline_value=base_v,
                    delta_pct=delta,
                    details_json=json.dumps(details, ensure_ascii=False),
                )
                db.add(a)
                created += 1

            if spend_delta is not None and spend_delta >= self.t.spend_spike_pct:
                add("spend_usd", spend_cur, spend_base, spend_delta, "yellow", {"type": "spend_spike"})
            if spend_delta is not None and spend_delta <= self.t.spend_drop_pct:
                add("spend_usd", spend_cur, spend_base, spend_delta, "yellow", {"type": "spend_drop"})
            if gmv_delta is not None and gmv_delta <= self.t.gmv_drop_pct:
                add("gmv", gmv_cur, gmv_base, gmv_delta, "red", {"type": "gmv_drop"})
            if roas_delta is not None and roas_delta <= self.t.roas_drop_pct:
                add("roas", roas_cur, roas_base, roas_delta, "red", {"type": "roas_drop"})

        db.commit()
        return created

