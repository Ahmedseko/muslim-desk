"""Qibla direction and distance to Mecca calculator."""
from __future__ import annotations
import math

KAABA_LAT = 21.4225   # degrees N
KAABA_LON = 39.8262   # degrees E
EARTH_RADIUS_KM = 6371.0


def qibla_bearing(latitude: float, longitude: float) -> float:
    """Bearing from location to Kaaba in degrees clockwise from North (0–360)."""
    lat1 = math.radians(latitude)
    lat2 = math.radians(KAABA_LAT)
    d_lon = math.radians(KAABA_LON - longitude)
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360.0) % 360.0


def distance_to_mecca_km(latitude: float, longitude: float) -> float:
    """Great-circle distance in km using Haversine formula."""
    lat1 = math.radians(latitude)
    lat2 = math.radians(KAABA_LAT)
    d_lat = math.radians(KAABA_LAT - latitude)
    d_lon = math.radians(KAABA_LON - longitude)
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compass_direction(bearing: float) -> str:
    """Convert bearing degrees to 16-point compass abbreviation."""
    dirs = ["U", "UTL", "TL", "TTL", "T", "TTG", "TG", "BTG",
            "S", "BSD", "SD", "BLD", "B", "BBL", "BL", "UBL"]
    return dirs[round(bearing / 22.5) % 16]
