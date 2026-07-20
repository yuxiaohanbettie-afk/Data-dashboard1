from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdFactDaily(Base):
    __tablename__ = "ad_fact_daily"

    __table_args__ = (
        UniqueConstraint("row_hash", name="uq_ad_fact_daily_row_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Core dimensions (from Excel)
    dt: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    site_code: Mapped[str] = mapped_column(String, nullable=False, index=True)  # country
    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)  # google/meta

    budget_type: Mapped[str | None] = mapped_column(String, nullable=True)
    attribution_modifier: Mapped[str | None] = mapped_column(String, nullable=True)

    account_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    account_name: Mapped[str | None] = mapped_column(String, nullable=True)

    campaign_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    campaign_name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    chan_first_cate_desc: Mapped[str | None] = mapped_column(String, nullable=True)
    chan_cate_cd: Mapped[str | None] = mapped_column(String, nullable=True)
    chan_cate_desc: Mapped[str | None] = mapped_column(String, nullable=True)

    # Parsed campaign dimensions (configurable parser output)
    business_unit: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    ad_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    industry: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    promotion: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    campaign_goal: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    optimization_target: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    campaign_date_code: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    campaign_dims_json: Mapped[str | None] = mapped_column(String, nullable=True)  # extra dims (JSON string)

    # Metrics (raw from Excel)
    impression: Mapped[float | None] = mapped_column(Float, nullable=True)
    click: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_gbp: Mapped[float | None] = mapped_column(Float, nullable=True)

    uv: Mapped[float | None] = mapped_column(Float, nullable=True)
    dau: Mapped[float | None] = mapped_column(Float, nullable=True)
    pdp_uv: Mapped[float | None] = mapped_column(Float, nullable=True)
    atc_uv: Mapped[float | None] = mapped_column(Float, nullable=True)
    settled_uv: Mapped[float | None] = mapped_column(Float, nullable=True)
    submitted_uv: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_install_uv: Mapped[float | None] = mapped_column(Float, nullable=True)

    parent_orders: Mapped[float | None] = mapped_column(Float, nullable=True)
    paid_users: Mapped[float | None] = mapped_column(Float, nullable=True)
    gmv: Mapped[float | None] = mapped_column(Float, nullable=True)

    new_parent_orders: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_paid_users: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_paid_users_gmv: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Dedup + lineage
    row_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

