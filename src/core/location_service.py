"""Geolocation service using ip-api.com (free, no key required)."""
from __future__ import annotations

import math
from dataclasses import dataclass

# Maps ISO 3166-1 alpha-2 country code → recommended prayer calculation method.
# Fallback for unmapped countries: MWL (Muslim World League — most universal).
_COUNTRY_METHOD: dict[str, str] = {
    # Indonesia
    "ID": "Kemenag",
    # Saudi Arabia & Gulf
    "SA": "Makkah", "AE": "Makkah", "KW": "Makkah", "BH": "Makkah",
    "QA": "Makkah", "OM": "Makkah", "YE": "Makkah",
    # Egypt, North Africa & Levant
    "EG": "Egypt", "LY": "Egypt", "DZ": "Egypt", "MA": "Egypt",
    "TN": "Egypt", "SD": "Egypt", "JO": "Egypt", "SY": "Egypt",
    "IQ": "Egypt", "LB": "Egypt", "PS": "Egypt",
    # South Asia
    "PK": "Karachi", "AF": "Karachi", "IN": "Karachi", "BD": "Karachi",
    # North America
    "US": "ISNA", "CA": "ISNA",
    # Southeast Asia — Singapore MUIS method
    "SG": "Singapore", "MY": "Singapore", "BN": "Singapore",
    # Iran
    "IR": "Tehran",
    # Turkey — MWL is used (Diyanet not in METHODS list)
}


def method_for_country(country_code: str) -> str:
    """Return the recommended prayer calculation method for an ISO country code."""
    return _COUNTRY_METHOD.get(country_code.upper(), "MWL")


@dataclass
class LocationInfo:
    latitude:      float = -6.2088
    longitude:     float = 106.8456
    city:          str   = "Jakarta"
    country:       str   = "Indonesia"
    country_code:  str   = "ID"
    timezone:      float = 7.0
    timezone_name: str   = "Asia/Jakarta"
    altitude:      float = 0.0

    def display_name(self) -> str:
        return f"{self.city}, {self.country}"


# Jakarta as safe default
_DEFAULT = LocationInfo()


def detect_location(timeout: int = 6) -> LocationInfo:
    """Auto-detect location via IP geolocation.  Returns default if offline."""
    try:
        import requests
        r = requests.get(
            "http://ip-api.com/json/",
            params={"fields": "lat,lon,city,country,countryCode,timezone,offset,status,message"},
            timeout=timeout,
        )
        data = r.json()
        if data.get("status") != "success":
            return _DEFAULT
        tz_hours = data.get("offset", 25200) / 3600.0
        return LocationInfo(
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
            city=data.get("city", "Unknown"),
            country=data.get("country", ""),
            country_code=data.get("countryCode", ""),
            timezone=tz_hours,
            timezone_name=data.get("timezone", ""),
        )
    except Exception:
        return _DEFAULT


def city_from_coords(lat: float, lon: float, timeout: int = 5) -> str:
    """Reverse-geocode coordinates to a city name (uses nominatim)."""
    try:
        import requests
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "MuslimDesk/1.0"},
            timeout=timeout,
        )
        data = r.json()
        addr = data.get("address", {})
        city = (addr.get("city")
                or addr.get("town")
                or addr.get("village")
                or addr.get("county")
                or "Unknown")
        country = addr.get("country", "")
        return f"{city}, {country}"
    except Exception:
        return f"{lat:.4f}, {lon:.4f}"


def local_timezone_offset() -> float:
    """Return local UTC offset in fractional hours using Python's stdlib."""
    import time as _time
    return -_time.timezone / 3600.0 if not _time.daylight else -_time.altzone / 3600.0


def app_now(app_timezone: float):
    """Current datetime adjusted to the app's configured timezone."""
    from datetime import datetime, timedelta
    diff = app_timezone - local_timezone_offset()
    return datetime.now() + timedelta(hours=diff)


def tz_label(offset: float) -> str:
    """Human-readable timezone label."""
    sign = "+" if offset >= 0 else ""
    h = int(abs(offset))
    m = int(round((abs(offset) - h) * 60))
    return f"UTC{sign}{h}" if m == 0 else f"UTC{sign}{h}:{m:02d}"


def timezone_from_longitude(lon: float) -> float:
    """Estimate UTC offset from longitude (nearest whole hour) — fallback only."""
    return float(round(lon / 15.0))


def timezone_from_coords(lat: float, lon: float) -> tuple[float, str]:
    """Return (utc_offset_hours, iana_name) for given coordinates.

    Uses timezonefinder for accurate political timezone boundaries.
    Falls back to longitude estimate if library unavailable.
    """
    try:
        from timezonefinder import TimezoneFinder
        from zoneinfo import ZoneInfo
        from datetime import datetime
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon) or ""
        if tz_name:
            offset = datetime.now(ZoneInfo(tz_name)).utcoffset().total_seconds() / 3600
            return offset, tz_name
    except Exception:
        pass
    return timezone_from_longitude(lon), ""


def search_city(query: str, timeout: int = 8) -> list[dict]:
    """Search for a city/place worldwide using Nominatim OpenStreetMap.

    Returns a list of dicts with keys:
        display_name, full_name, lat, lon, city, country, country_code, timezone, timezone_name.
    """
    try:
        import requests
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 10,
                "addressdetails": 1,
            },
            headers={"User-Agent": "MuslimDesk/1.0 (prayer time app; worldwide)"},
            timeout=timeout,
        )
        results = r.json()
        out = []
        for item in results:
            lat = float(item["lat"])
            lon = float(item["lon"])
            addr = item.get("address", {})

            # Build a readable place name from address components
            city = (
                addr.get("village")
                or addr.get("suburb")
                or addr.get("town")
                or addr.get("city")
                or addr.get("municipality")
                or addr.get("county")
                or addr.get("state_district")
                or addr.get("state")
                or item.get("display_name", "").split(",")[0]
            )
            district = (
                addr.get("county")
                or addr.get("state_district")
                or addr.get("municipality")
                or ""
            )
            country      = addr.get("country", "")
            country_code = addr.get("country_code", "").upper()
            state        = addr.get("state", "")

            # Short display: Place, District/State, Country (max 3 parts after city)
            parts = [p for p in [district, state, country] if p and p != city]
            display = city + (", " + ", ".join(parts[:2]) if parts else "")

            tz_offset, tz_name = timezone_from_coords(lat, lon)
            out.append({
                "display_name":  display,
                "full_name":     item.get("display_name", display),
                "lat":           lat,
                "lon":           lon,
                "city":          city,
                "country":       country,
                "country_code":  country_code,
                "timezone":      tz_offset,
                "timezone_name": tz_name,
            })
        return out
    except Exception:
        return []
