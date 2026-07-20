from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from app.adapters import excel_cb1_7d_mkt_seller_v1 as adapter_v1
from app.models import AdFactDaily, Upload
from app.services.campaign_parser import CampaignNameParser
from app.utils.hashing import sha1_json, sha256_file


@dataclass
class ImportResult:
    upload_id: int
    rows_total: int
    rows_imported: int
    rows_skipped: int
    db_total_rows: int
    latest_upload_time: datetime


class ImportService:
    def __init__(self, campaign_parser: CampaignNameParser):
        self.parser = campaign_parser

    def import_excel(self, db: Session, file_path: str) -> ImportResult:
        p = Path(file_path)
        file_sha = sha256_file(str(p))

        df = pd.read_excel(str(p), sheet_name=0)
        if not adapter_v1.matches(df):
            raise ValueError(
                "Excel schema not recognized. Expected fixed columns for CB1_7D_mkt_seller_v1."
            )

        df = adapter_v1.normalize(df)
        records = adapter_v1.to_records(df)

        upload = Upload(filename=p.name, file_sha256=file_sha, rows_total=len(records))
        db.add(upload)
        db.flush()  # assign id

        to_insert: list[dict[str, Any]] = []
        for r in records:
            parsed = self.parser.parse(r.get("campaign_name") or "")
            dims_json = json.dumps(parsed.extra or {}, ensure_ascii=False)

            row_key = {
                # include all source columns to make "same data re-upload" idempotent
                k: r.get(k)
                for k in adapter_v1.SCHEMA.expected_columns
                if k in r
            }
            row_hash = sha1_json(row_key)

            to_insert.append(
                {
                    "dt": r.get("dt"),
                    "site_code": r.get("site_code"),
                    "platform": (r.get("platform") or "").lower(),
                    "budget_type": r.get("budget_type"),
                    "attribution_modifier": r.get("attribution_modifier"),
                    "account_id": str(r.get("account_id")) if r.get("account_id") is not None else None,
                    "account_name": r.get("account_name"),
                    "campaign_id": str(r.get("campaign_id")) if r.get("campaign_id") is not None else None,
                    "campaign_name": r.get("campaign_name") or "",
                    "chan_first_cate_desc": r.get("chan_first_cate_desc"),
                    "chan_cate_cd": str(r.get("chan_cate_cd")) if r.get("chan_cate_cd") is not None else None,
                    "chan_cate_desc": r.get("chan_cate_desc"),
                    "business_unit": parsed.business_unit,
                    "ad_type": parsed.ad_type,
                    "country": parsed.country,
                    "industry": parsed.industry,
                    "promotion": parsed.promotion,
                    "language": parsed.language,
                    "campaign_goal": parsed.campaign_goal,
                    "optimization_target": parsed.optimization_target,
                    "campaign_date_code": parsed.campaign_date_code,
                    "campaign_dims_json": dims_json,
                    "impression": r.get("impression"),
                    "click": r.get("click"),
                    "cost_eur": r.get("cost_eur"),
                    "cost_usd": r.get("cost_usd"),
                    "cost_gbp": r.get("cost_gbp"),
                    "uv": r.get("uv"),
                    "dau": r.get("dau"),
                    "pdp_uv": r.get("pdp_uv"),
                    "atc_uv": r.get("atc_uv"),
                    "settled_uv": r.get("settled_uv"),
                    "submitted_uv": r.get("submitted_uv"),
                    "new_install_uv": r.get("new_install_uv"),
                    "parent_orders": r.get("parent_orders"),
                    "paid_users": r.get("paid_users"),
                    "gmv": r.get("gmv"),
                    "new_parent_orders": r.get("new_parent_orders"),
                    "new_paid_users": r.get("new_paid_users"),
                    "new_paid_users_gmv": r.get("new_paid_users_gmv"),
                    "row_hash": row_hash,
                }
            )

        rows_imported = 0
        chunk_size = 200  # avoid SQLite max-parameters limit
        for i in range(0, len(to_insert), chunk_size):
            chunk = to_insert[i : i + chunk_size]
            stmt = insert(AdFactDaily).values(chunk)
            # SQLite dedupe: unique(row_hash) + OR IGNORE
            stmt = stmt.prefix_with("OR IGNORE")
            res = db.execute(stmt)
            rows_imported += int(res.rowcount or 0)

        rows_skipped = len(to_insert) - rows_imported

        upload.rows_imported = rows_imported
        upload.rows_skipped = rows_skipped
        db.add(upload)
        db.commit()

        db_total_rows = int(db.scalar(select(func.count()).select_from(AdFactDaily)) or 0)
        latest_upload_time = upload.uploaded_at

        return ImportResult(
            upload_id=upload.id,
            rows_total=len(to_insert),
            rows_imported=rows_imported,
            rows_skipped=rows_skipped,
            db_total_rows=db_total_rows,
            latest_upload_time=latest_upload_time,
        )
