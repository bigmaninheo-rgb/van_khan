from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    "ten_be": "",
    "dia_chi": "Quế Võ, Bắc Ninh",
    "ngay_thang": "",
    "ngay_am_lich": "",
    "year": 2026,
}


def load_config(config_path: str | Path = "config.json") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()
    return {**DEFAULT_CONFIG, **raw}


def save_config(data: Dict[str, Any], config_path: str | Path = "config.json") -> None:
    path = Path(config_path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
