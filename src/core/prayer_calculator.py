"""Prayer time calculator based on PrayTimes.org algorithm.

Supports multiple calculation methods and both Shafi'i & Hanafi Asr rules.
"""
from __future__ import annotations

import math
from datetime import date, datetime

PRAYER_NAMES_ID = {
    "Fajr": "Subuh",
    "Sunrise": "Syuruk",
    "Dhuhr": "Dzuhur",
    "Asr": "Ashar",
    "Maghrib": "Maghrib",
    "Isha": "Isya",
    "Imsak": "Imsak",
}

HIJRI_MONTHS_ID = [
    "Muharram", "Safar", "Rabi'ul Awal", "Rabi'ul Akhir",
    "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban",
    "Ramadhan", "Syawal", "Dzulqa'dah", "Dzulhijjah",
]

DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Ahad"]
MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

# Islamic events by Hijri (month, day): name in Indonesian / English
ISLAMIC_EVENTS: dict[tuple[int, int], dict[str, str]] = {
    (1,  1):  {"id": "Tahun Baru Hijriah",    "en": "Islamic New Year"},
    (1,  10): {"id": "Hari Asyura",            "en": "Day of Ashura"},
    (3,  12): {"id": "Maulid Nabi ﷺ",         "en": "Prophet's Birthday ﷺ"},
    (7,  27): {"id": "Isra Mi'raj",            "en": "Isra Mi'raj"},
    (8,  15): {"id": "Nisfu Sya'ban",          "en": "Nisf Sha'ban"},
    (9,  1):  {"id": "Awal Ramadhan",          "en": "Start of Ramadan"},
    (9,  17): {"id": "Nuzulul Qur'an",         "en": "Nuzul al-Quran"},
    (9,  27): {"id": "Malam Lailatul Qadr",    "en": "Laylat al-Qadr"},
    (10, 1):  {"id": "Idul Fitri",             "en": "Eid al-Fitr"},
    (10, 2):  {"id": "Idul Fitri Hari Ke-2",   "en": "Eid al-Fitr Day 2"},
    (10, 3):  {"id": "Hari Tasyrik",           "en": "Day of Tashreek"},
    (12, 9):  {"id": "Hari Arafah",            "en": "Day of Arafah"},
    (12, 10): {"id": "Idul Adha",              "en": "Eid al-Adha"},
    (12, 11): {"id": "Hari Tasyrik",           "en": "Day of Tashreek"},
    (12, 12): {"id": "Hari Tasyrik",           "en": "Day of Tashreek"},
    (12, 13): {"id": "Hari Tasyrik",           "en": "Day of Tashreek"},
}

# isha_min=True means Isha is N minutes after Maghrib (fixed), else sun angle
METHODS: dict[str, dict] = {
    "Kemenag":   {"name": "Kemenag Indonesia",                          "fajr": 20.0, "isha": 18.0, "isha_min": False},
    "MWL":       {"name": "Muslim World League",                        "fajr": 18.0, "isha": 17.0, "isha_min": False},
    "ISNA":      {"name": "ISNA (Amerika Utara)",                       "fajr": 15.0, "isha": 15.0, "isha_min": False},
    "Egypt":     {"name": "Otoritas Mesir",                             "fajr": 19.5, "isha": 17.5, "isha_min": False},
    "Makkah":    {"name": "Umm al-Qura (Makkah)",                      "fajr": 18.5, "isha": 90.0, "isha_min": True},
    "Karachi":   {"name": "Univ. Islamic Sciences, Karachi",            "fajr": 18.0, "isha": 18.0, "isha_min": False},
    "Tehran":    {"name": "Institute of Geophysics, Tehran",            "fajr": 17.7, "isha": 14.0, "isha_min": False},
    "Singapore": {"name": "MUIS Singapore",                             "fajr": 20.0, "isha": 18.0, "isha_min": False},
}

ASR_STANDARD = 1  # Shafi'i / Maliki / Hanbali
ASR_HANAFI   = 2  # Hanafi


def _sin(d: float) -> float: return math.sin(math.radians(d))
def _cos(d: float) -> float: return math.cos(math.radians(d))
def _tan(d: float) -> float: return math.tan(math.radians(d))
def _arcsin(x: float) -> float: return math.degrees(math.asin(x))
def _arccos(x: float) -> float: return math.degrees(math.acos(x))
def _arctan2(y: float, x: float) -> float: return math.degrees(math.atan2(y, x))
def _arccot(x: float) -> float: return math.degrees(math.atan(1.0 / x))
def _fix_hour(h: float) -> float: return h - 24.0 * math.floor(h / 24.0)
def _fix_angle(a: float) -> float: return a - 360.0 * math.floor(a / 360.0)


def _julian_day(year: int, month: int, day: int) -> float:
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100.0)
    B = 2 - A + math.floor(A / 4.0)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5


def _sun_position(jd: float) -> tuple[float, float]:
    """Return (declination_deg, equation_of_time_hours)."""
    D = jd - 2451545.0
    g = _fix_angle(357.529 + 0.98560028 * D)
    q = _fix_angle(280.459 + 0.98564736 * D)
    L = _fix_angle(q + 1.915 * _sin(g) + 0.020 * _sin(2 * g))
    e = 23.439 - 0.00000036 * D
    RA = _fix_hour(_arctan2(_cos(e) * _sin(L), _cos(L)) / 15.0)
    d  = _arcsin(_sin(e) * _sin(L))
    EqT = q / 15.0 - RA
    return d, EqT


def _solar_noon(jd: float, longitude: float, timezone: float) -> float:
    _, EqT = _sun_position(jd)
    return 12.0 + timezone - longitude / 15.0 - EqT


def _sun_angle_time(jd: float, latitude: float, angle: float,
                    noon: float, cw: bool = False) -> float:
    d, _ = _sun_position(jd)
    cos_val = (-_sin(angle) - _sin(d) * _sin(latitude)) / (_cos(d) * _cos(latitude))
    cos_val = max(-1.0, min(1.0, cos_val))
    t = _arccos(cos_val) / 15.0
    return noon + (t if cw else -t)


def _asr_time(jd: float, latitude: float, shadow: int, noon: float) -> float:
    d, _ = _sun_position(jd)
    angle = -_arccot(shadow + _tan(abs(latitude - d)))
    return _sun_angle_time(jd, latitude, angle, noon, cw=True)


def _h_to_hhmm(h: float) -> str:
    h = _fix_hour(h)
    hrs = int(h)
    mins = int(round((h - hrs) * 60.0))
    if mins == 60:
        hrs += 1
        mins = 0
    hrs = hrs % 24
    return f"{hrs:02d}:{mins:02d}"


def calculate_times(
    d: date,
    latitude: float,
    longitude: float,
    timezone: float,
    method: str = "Kemenag",
    asr_method: int = ASR_STANDARD,
    altitude: float = 0.0,
    imsak_minutes: int = 0,
) -> dict[str, str]:
    """Return prayer times as HH:MM strings for the given date/location."""
    m   = METHODS.get(method, METHODS["Kemenag"])
    jd  = _julian_day(d.year, d.month, d.day)
    noon = _solar_noon(jd, longitude, timezone)
    alt_corr = 0.0347 * math.sqrt(max(0.0, altitude))

    fajr    = _sun_angle_time(jd, latitude, m["fajr"] + alt_corr, noon, cw=False)
    sunrise = _sun_angle_time(jd, latitude, 0.833 + alt_corr,     noon, cw=False)
    dhuhr   = noon
    asr     = _asr_time(jd, latitude, asr_method, noon)
    maghrib = _sun_angle_time(jd, latitude, 0.833 + alt_corr,     noon, cw=True)
    isha    = (maghrib + m["isha"] / 60.0
               if m["isha_min"]
               else _sun_angle_time(jd, latitude, m["isha"] + alt_corr, noon, cw=True))

    result: dict[str, str] = {}
    if imsak_minutes > 0:
        result["Imsak"] = _h_to_hhmm(fajr - imsak_minutes / 60.0)
    result["Fajr"]    = _h_to_hhmm(fajr)
    result["Sunrise"] = _h_to_hhmm(sunrise)
    result["Dhuhr"]   = _h_to_hhmm(dhuhr)
    result["Asr"]     = _h_to_hhmm(asr)
    result["Maghrib"] = _h_to_hhmm(maghrib)
    result["Isha"]    = _h_to_hhmm(isha)
    return result


def times_as_datetime(
    d: date,
    latitude: float,
    longitude: float,
    timezone: float,
    method: str = "Kemenag",
    asr_method: int = ASR_STANDARD,
    altitude: float = 0.0,
) -> dict[str, datetime]:
    """Return prayer times as datetime objects (no Imsak — used for alarm checks)."""
    raw = calculate_times(d, latitude, longitude, timezone, method, asr_method, altitude)
    result: dict[str, datetime] = {}
    for name, tv in raw.items():
        h, m = map(int, tv.split(":"))
        result[name] = datetime(d.year, d.month, d.day, h, m)
    return result


def gregorian_to_hijri(year: int, month: int, day: int) -> tuple[int, int, int]:
    """Convert Gregorian date to Hijri using hijri-converter or built-in fallback."""
    try:
        from hijri_converter import Gregorian
        h = Gregorian(year, month, day).to_hijri()
        return h.year, h.month, h.day
    except Exception:
        return _gregorian_to_hijri_fallback(year, month, day)


def _gregorian_to_hijri_fallback(year: int, month: int, day: int) -> tuple[int, int, int]:
    """Tabular Islamic Calendar fallback (±1 day from moon sighting)."""
    jd = _julian_day(year, month, day) + 0.5
    z  = int(jd)
    L  = z - 1948438
    N  = (L - 1) // 10631
    L  = L - 10631 * N
    J  = (L - 1) // 354 + 1 if L > 354 else 0
    L  = L - int(354.367 * J + 0.5) if J else L
    I  = (L + 29) // 30
    dy = int(L - int(29.5001 * I + 0.5) + 1)
    mo = int(I if I <= 12 else I - 12)
    yr = int(N * 30 + J + (1 if I > 12 else 0))
    return yr, mo, dy


def hijri_month_name(month: int) -> str:
    if 1 <= month <= 12:
        return HIJRI_MONTHS_ID[month - 1]
    return str(month)


def format_hijri(year: int, month: int, day: int) -> str:
    return f"{day} {hijri_month_name(month)} {year} H"


def day_name_id(weekday: int) -> str:
    """weekday: Monday=0 … Sunday=6"""
    return DAYS_ID[weekday % 7]


def month_name_id(month: int) -> str:
    return MONTHS_ID[(month - 1) % 12]


def get_islamic_event(hijri_month: int, hijri_day: int, lang: str = "id") -> str | None:
    """Return event name for the given Hijri date, or None if no event."""
    ev = ISLAMIC_EVENTS.get((hijri_month, hijri_day))
    if ev:
        return ev.get(lang, ev.get("id", ""))
    return None
