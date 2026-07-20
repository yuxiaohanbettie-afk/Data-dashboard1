from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ParsedCampaign:
    business_unit: str | None = None
    ad_type: str | None = None
    country: str | None = None
    industry: str | None = None
    promotion: str | None = None
    language: str | None = None
    campaign_goal: str | None = None
    optimization_target: str | None = None
    campaign_date_code: str | None = None
    extra: dict[str, Any] | None = None


class CampaignNameParser:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self._config = self._load()

        rx = self._config.get("regex", {})
        self._rx_country = re.compile(rx.get("country", r"^[A-Z]{2}$"))
        self._rx_language = re.compile(rx.get("language", r"^[a-z]{2}$"))
        self._rx_date = re.compile(rx.get("date_code", r"^\d{6}$"))
        self._rx_bu = re.compile(rx.get("business_unit", r"^(CB\d+|CB1)$"))

        self._known_ad_types = set(self._config.get("known_ad_types", []))
        self._known_goals = set(self._config.get("known_goals", []))
        self._promotion_tokens = set(self._config.get("promotion_tokens", []))
        self._opt_prefixes = tuple(self._config.get("optimization_prefixes", []))

    def _load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def parse(self, campaign_name: str) -> ParsedCampaign:
        raw = (campaign_name or "").strip()
        if not raw:
            return ParsedCampaign(extra={"tokens": []})

        delimiters = self._config.get("delimiters", ["-"])
        tokens = [raw]
        for d in delimiters:
            if len(tokens) == 1:
                tokens = [t for t in raw.split(d) if t != ""]
                if len(tokens) > 1:
                    break

        p = ParsedCampaign(extra={"tokens": tokens})

        # 1) Regex-based tokens
        for t in tokens:
            if p.country is None and self._rx_country.match(t):
                p.country = t
            if p.language is None and self._rx_language.match(t):
                p.language = t
            if p.campaign_date_code is None and self._rx_date.match(t):
                p.campaign_date_code = t
            if p.business_unit is None and self._rx_bu.match(t):
                p.business_unit = t

        # 2) Known lists
        for t in tokens:
            if p.ad_type is None and t in self._known_ad_types:
                p.ad_type = t
            if p.campaign_goal is None and t in self._known_goals:
                p.campaign_goal = t
            if p.promotion is None and t in self._promotion_tokens:
                p.promotion = t

        # 3) Optimization target: ROAS300% / Roas200% ...
        for t in tokens:
            if p.optimization_target is None and any(t.startswith(pref) for pref in self._opt_prefixes):
                p.optimization_target = t

        # 4) Industry heuristic:
        # If token after country is non-empty and not recognized, treat as industry.
        try:
            if p.industry is None and p.country in tokens:
                idx = tokens.index(p.country)
                cand = tokens[idx + 1] if idx + 1 < len(tokens) else None
                if cand and cand not in self._known_ad_types and cand not in self._known_goals and cand not in self._promotion_tokens:
                    if not self._rx_date.match(cand) and not self._rx_language.match(cand) and not self._rx_country.match(cand):
                        p.industry = cand
        except Exception:
            pass

        return p

