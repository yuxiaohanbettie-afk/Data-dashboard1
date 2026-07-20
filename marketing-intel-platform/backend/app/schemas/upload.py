from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UploadImportResponse(BaseModel):
    upload_id: int
    rows_total: int
    rows_imported: int
    rows_skipped: int
    db_total_rows: int
    latest_upload_time: datetime

