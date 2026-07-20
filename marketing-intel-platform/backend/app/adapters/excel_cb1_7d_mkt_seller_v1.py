from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ExcelSchema:
    name: str
    expected_columns: tuple[str, ...]


SCHEMA = ExcelSchema(
    name="CB1_7D_mkt_seller_v1",
    expected_columns=(
        "dt",
        "site_code",
        "budget_type",
        "attribution_modifier",
        "account_id",
        "account_name",
        "campaign_id",
        "campaign_name",
        "chan_first_cate_desc",
        "chan_cate_cd",
        "chan_cate_desc",
        "Impression",
        "Click",
        "Cost_ad_eur_amt",
        "Cost_ad_usd_amt",
        "Cost_ad_gbp_amt",
        "UV",
        "DAU",
        "PDP_UV",
        "ATC_UV",
        "Settled_UV",
        "Submitted_UV",
        "New_Install_UV",
        "Parent_Orders",
        "PaidUsers",
        "GMV",
        "New_Parent_Orders",
        "New_Paid_Users",
        "New_Paid_Users_GMV",
    ),
)


def matches(df: pd.DataFrame) -> bool:
    cols = tuple(str(c).strip() for c in df.columns)
    return cols == SCHEMA.expected_columns


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize datatypes + rename into internal canonical column names.
    IMPORTANT: do NOT ask user to change Excel. We adapt here.
    """
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]

    out = out.rename(
        columns={
            "Impression": "impression",
            "Click": "click",
            "Cost_ad_eur_amt": "cost_eur",
            "Cost_ad_usd_amt": "cost_usd",
            "Cost_ad_gbp_amt": "cost_gbp",
            "UV": "uv",
            "DAU": "dau",
            "PDP_UV": "pdp_uv",
            "ATC_UV": "atc_uv",
            "Settled_UV": "settled_uv",
            "Submitted_UV": "submitted_uv",
            "New_Install_UV": "new_install_uv",
            "Parent_Orders": "parent_orders",
            "PaidUsers": "paid_users",
            "GMV": "gmv",
            "New_Parent_Orders": "new_parent_orders",
            "New_Paid_Users": "new_paid_users",
            "New_Paid_Users_GMV": "new_paid_users_gmv",
        }
    )

    out["dt"] = pd.to_datetime(out["dt"], errors="coerce").dt.date
    out["site_code"] = out["site_code"].astype(str)
    out["campaign_name"] = out["campaign_name"].astype(str)

    # Platform: prefer chan_cate_desc if present (google/meta)
    out["platform"] = out.get("chan_cate_desc", pd.Series([None] * len(out))).astype(str)

    return out


def to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.where(pd.notna(df), None).to_dict(orient="records")

