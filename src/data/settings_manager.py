"""Persistent settings stored in ~/.muslim_desk/settings.json."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict

SETTINGS_PATH = Path.home() / ".muslim_desk" / "settings.json"
_STARTUP_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
_STARTUP_NAME = "Muslim Desk"


def set_startup_enabled(enabled: bool) -> bool:
    """Add or remove the Windows startup registry entry."""
    import sys, winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _STARTUP_KEY, 0,
            winreg.KEY_SET_VALUE,
        )
        if enabled:
            exe = sys.executable  # correct when frozen by PyInstaller
            winreg.SetValueEx(key, _STARTUP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        else:
            try:
                winreg.DeleteValue(key, _STARTUP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def is_startup_enabled() -> bool:
    """Return True if app is registered to run at Windows startup."""
    import winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _STARTUP_KEY, 0,
            winreg.KEY_READ,
        )
        winreg.QueryValueEx(key, _STARTUP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


@dataclass
class Settings:
    # Appearance
    theme: str = "dark"           # dark | light | system

    # Prayer calculation
    method: str   = "Kemenag"
    asr_method: int = 1           # 1=Standard (Syafi'i), 2=Hanafi

    # Location
    latitude:       float = -6.2088
    longitude:      float = 106.8456
    city:           str   = "Jakarta"
    country:        str   = "Indonesia"
    timezone:       float = 7.0
    timezone_name:  str   = "Asia/Jakarta"
    altitude:       float = 0.0
    auto_location:  bool  = True

    # Notification / alarm
    notification_enabled: bool = True
    sound_enabled:        bool = True
    custom_sound_path:    str  = ""
    reminder_minutes:     int  = 5     # 0=off, else N minutes before each prayer

    # Per-prayer alarm on/off (True = enabled)
    prayer_alarms: Dict[str, bool] = field(default_factory=lambda: {
        "Fajr":    True,
        "Sunrise": False,
        "Dhuhr":   True,
        "Asr":     True,
        "Maghrib": True,
        "Isha":    True,
    })

    # Per-prayer custom sound path (empty = use global custom_sound_path or default)
    prayer_sounds: Dict[str, str] = field(default_factory=lambda: {
        "Fajr":    "",
        "Sunrise": "",
        "Dhuhr":   r"C:\Users\ahmedseko\Music\ADZAN UMAR AL FARUQ.wav",
        "Asr":     r"C:\Users\ahmedseko\Music\ADZAN UMAR AL FARUQ.wav",
        "Maghrib": r"C:\Users\ahmedseko\Music\ADZAN UMAR AL FARUQ.wav",
        "Isha":    r"C:\Users\ahmedseko\Music\ADZAN UMAR AL FARUQ.wav",
    })

    # Time display format
    time_format: str = "24h"   # "24h" | "12h"

    # Language
    language: str = "id"       # "id" | "en"

    # Window state
    start_minimized: bool = False
    minimize_to_tray: bool = True


def load() -> Settings:
    try:
        if SETTINGS_PATH.exists():
            raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            s = Settings()
            for k, v in raw.items():
                if hasattr(s, k):
                    setattr(s, k, v)
            # ensure all prayer keys present
            defaults = Settings().prayer_alarms
            for key, default_val in defaults.items():
                s.prayer_alarms.setdefault(key, default_val)
            # safety: if all wajib prayers are disabled, reset to defaults
            _wajib = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
            if not any(s.prayer_alarms.get(p, False) for p in _wajib):
                for p in _wajib:
                    s.prayer_alarms[p] = True
            # ensure prayer_sounds keys present
            if not isinstance(s.prayer_sounds, dict):
                s.prayer_sounds = {}
            sound_defaults = Settings().prayer_sounds
            for key, default_val in sound_defaults.items():
                s.prayer_sounds.setdefault(key, default_val)
            return s
    except Exception:
        pass
    return Settings()


def save(settings: Settings) -> None:
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(
            json.dumps(asdict(settings), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass
