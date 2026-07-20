from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha1_json(obj: Any) -> str:
    raw = json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,  # dates/decimals -> stable string
    ).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()
