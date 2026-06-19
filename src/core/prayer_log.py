"""Prayer log — tracks daily sholat completion, persists to JSON."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

_LOG_FILE    = Path.home() / ".muslim_desk" / "prayer_log.json"
MAIN_PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]


def _read_all() -> dict:
    try:
        return json.loads(_LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_all(data: dict) -> None:
    try:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Keep only last 60 days to avoid unbounded growth
        if len(data) > 60:
            keys = sorted(data.keys())[-60:]
            data = {k: data[k] for k in keys}
        _LOG_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def load_today() -> dict[str, bool]:
    today = date.today().isoformat()
    return _read_all().get(today, {p: False for p in MAIN_PRAYERS})


def save_today(log: dict[str, bool]) -> None:
    data = _read_all()
    data[date.today().isoformat()] = log
    _write_all(data)


def load_streak() -> int:
    """Return consecutive days (including today) with all 5 prayers completed."""
    data = _read_all()
    streak = 0
    d = date.today()
    for _ in range(365):
        day_log = data.get(d.isoformat(), {})
        if all(day_log.get(p, False) for p in MAIN_PRAYERS):
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak
