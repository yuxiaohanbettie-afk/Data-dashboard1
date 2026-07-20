from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Anomaly
from app.schemas.anomaly import AnomalyOut

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=list[AnomalyOut])
def list_anomalies(
    start: date | None = Query(None),
    end: date | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = select(Anomaly).order_by(desc(Anomaly.detected_at)).limit(limit)
    if start:
        q = q.where(Anomaly.dt >= start)
    if end:
        q = q.where(Anomaly.dt <= end)
    rows = db.execute(q).scalars().all()
    return [AnomalyOut.model_validate(r, from_attributes=True) for r in rows]

