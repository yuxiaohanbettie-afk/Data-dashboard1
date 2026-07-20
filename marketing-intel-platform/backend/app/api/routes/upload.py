from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.upload import UploadImportResponse
from app.services.anomaly_detector import AnomalyDetector
from app.services.campaign_parser import CampaignNameParser
from app.services.import_service import ImportService

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/excel", response_model=UploadImportResponse)
def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx is supported")

    uploads_dir = (Path(__file__).resolve().parents[4] / "data" / "uploads").resolve()
    uploads_dir.mkdir(parents=True, exist_ok=True)
    dst = uploads_dir / file.filename

    with dst.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    parser_cfg = (Path(__file__).resolve().parents[4] / "config" / "campaign_parser.json").resolve()
    parser = CampaignNameParser(parser_cfg)
    svc = ImportService(parser)

    try:
        result = svc.import_excel(db, str(dst))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Run anomaly detection for latest date in file (assume file is daily rows)
    try:
        import pandas as pd

        df = pd.read_excel(str(dst), sheet_name=0, usecols=["dt"])
        dt_max = pd.to_datetime(df["dt"], errors="coerce").dt.date.max()
        if dt_max:
            AnomalyDetector().run_for_date(db, dt_max)
    except Exception:
        # Don't fail import if anomaly job fails
        pass

    return UploadImportResponse(**result.__dict__)

