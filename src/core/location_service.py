"""Geolocation service using ip-api.com (free, no key required)."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class LocationInfo:
    latitude: float      = -6.2088
    longitude: float     = 106.8456
    city: str            = "Jakarta"
    country: str         = "Indonesia"
    timezone: float      = 7.0
    timezone_name: str   = "Asia/Jakarta"
    altitude: float      = 0.0

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
            params={"fields": "lat,lon,city,country,timezone,offset,status,message"},
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
    """Current datetime adjusted to the app's configured timezone.

    Fixes the case where the system clock is in a different timezone than
    the selected prayer location (e.g. laptop on WIB but location is WITA).
    """
    from datetime import datetime, timedelta
    diff = app_timezone - local_timezone_offset()
    return datetime.now() + timedelta(hours=diff)


def tz_label(offset: float) -> str:
    """Human-readable timezone label for Indonesian and common offsets."""
    mapping = {
        7.0: "WIB (UTC+7)",
        8.0: "WITA (UTC+8)",
        9.0: "WIT (UTC+9)",
        5.5: "IST (UTC+5:30)",
        3.0: "UTC+3",
        0.0: "UTC",
    }
    if offset in mapping:
        return mapping[offset]
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
    """Search for a city/district using Nominatim OpenStreetMap.

    Returns a list of dicts with keys: display_name, lat, lon, timezone, city, country.
    Supports Indonesian place names including kecamatan/kabupaten.
    """
    try:
        import requests
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 8,
                "addressdetails": 1,
            },
            headers={"User-Agent": "MuslimDesk/1.0 (prayer time app)"},
            timeout=timeout,
        )
        results = r.json()
        out = []
        for item in results:
            lat = float(item["lat"])
            lon = float(item["lon"])
            addr = item.get("address", {})

            # Build a readable city name from the address components
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
            # Include district/regency if different
            district = (
                addr.get("county")
                or addr.get("state_district")
                or addr.get("municipality")
                or ""
            )
            country  = addr.get("country", "")
            state    = addr.get("state", "")

            # Build short display: Village, Kabupaten, Provinsi, Negara
            parts = [p for p in [city, district, state, country] if p and p != city]
            display = city + (", " + ", ".join(parts[:3]) if parts else "")

            tz_offset, tz_name = timezone_from_coords(lat, lon)
            out.append({
                "display_name": display,
                "full_name":    item.get("display_name", display),
                "lat":          lat,
                "lon":          lon,
                "city":         city,
                "country":      country,
                "timezone":     tz_offset,
                "timezone_name": tz_name,
            })
        return out
    except Exception:
        return []
