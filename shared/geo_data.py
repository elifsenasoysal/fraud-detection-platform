"""
Geographic data for Turkish cities.
Used for location-based anomaly detection (impossible travel check).
"""

import math
from typing import Optional


# ──────────────────────────────────────────
# City coordinates (latitude, longitude)
# ──────────────────────────────────────────
CITY_COORDINATES: dict[str, tuple[float, float]] = {
    # Marmara
    "Istanbul": (41.0082, 28.9784),
    "Bursa": (40.1885, 29.0610),
    "Kocaeli": (40.8533, 29.8815),
    "Edirne": (41.6818, 26.5623),
    "Tekirdag": (41.2824, 27.5120),
    "Balikesir": (39.6484, 27.8826),
    "Canakkale": (40.1553, 26.4142),
    "Sakarya": (40.6940, 30.4358),
    "Yalova": (40.6560, 29.2756),

    # İç Anadolu
    "Ankara": (39.9334, 32.8597),
    "Konya": (37.8746, 32.4932),
    "Eskisehir": (39.7667, 30.5256),
    "Kayseri": (38.7312, 35.4787),
    "Sivas": (39.7477, 37.0179),
    "Kirsehir": (39.1425, 34.1709),
    "Nevsehir": (38.6939, 34.6857),
    "Aksaray": (38.3687, 34.0370),
    "Karaman": (37.1759, 33.2287),

    # Ege
    "Izmir": (38.4192, 27.1287),
    "Antalya": (36.8969, 30.7133),
    "Mugla": (37.2153, 28.3636),
    "Denizli": (37.7765, 29.0864),
    "Aydin": (37.8560, 27.8416),
    "Manisa": (38.6191, 27.4289),
    "Kutahya": (39.4167, 29.9833),
    "Afyon": (38.7507, 30.5567),
    "Usak": (38.6823, 29.4082),
    "Burdur": (37.7203, 30.2908),
    "Isparta": (37.7648, 30.5566),

    # Karadeniz
    "Trabzon": (41.0027, 39.7168),
    "Samsun": (41.2867, 36.3300),
    "Rize": (41.0201, 40.5234),
    "Ordu": (40.9839, 37.8764),
    "Giresun": (40.9128, 38.3895),
    "Artvin": (41.1828, 41.8183),
    "Zonguldak": (41.4564, 31.7987),
    "Kastamonu": (41.3887, 33.7827),
    "Sinop": (42.0231, 35.1531),
    "Amasya": (40.6499, 35.8353),
    "Tokat": (40.3167, 36.5544),

    # Güneydoğu
    "Gaziantep": (37.0662, 37.3833),
    "Diyarbakir": (37.9144, 40.2306),
    "Sanliurfa": (37.1674, 38.7955),
    "Mardin": (37.3212, 40.7245),
    "Adiyaman": (37.7648, 38.2786),
    "Siirt": (37.9333, 41.9500),
    "Batman": (37.8812, 41.1351),
    "Sirnak": (37.4187, 42.4918),

    # Doğu Anadolu
    "Erzurum": (39.9054, 41.2658),
    "Van": (38.4891, 43.3800),
    "Malatya": (38.3552, 38.3095),
    "Elazig": (38.6810, 39.2264),
    "Erzincan": (39.7500, 39.5000),
    "Kars": (40.6013, 43.0975),
    "Agri": (39.7191, 43.0503),
    "Mus": (38.9462, 41.7539),
    "Bingol": (38.8854, 40.4966),
    "Bitlis": (38.3938, 42.1232),
    "Hakkari": (37.5833, 43.7333),
    "Igdir": (39.9167, 44.0500),
    "Tunceli": (39.1079, 39.5401),

    # Akdeniz
    "Adana": (37.0000, 35.3213),
    "Mersin": (36.8121, 34.6415),
    "Hatay": (36.2025, 36.1604),
    "Kahramanmaras": (37.5858, 36.9371),
    "Osmaniye": (37.0742, 36.2478),
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth.

    Args:
        lat1, lon1: Coordinates of point 1 (degrees)
        lat2, lon2: Coordinates of point 2 (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_city_coordinates(city_name: str) -> Optional[tuple[float, float]]:
    """Get coordinates for a Turkish city (case-insensitive).

    Args:
        city_name: Name of the city

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Try exact match first
    if city_name in CITY_COORDINATES:
        return CITY_COORDINATES[city_name]

    # Try case-insensitive match
    city_lower = city_name.lower()
    for name, coords in CITY_COORDINATES.items():
        if name.lower() == city_lower:
            return coords

    return None


def is_impossible_travel(
    city1: str,
    city2: str,
    time_diff_seconds: float,
    max_speed_kmh: float = 900.0,
) -> bool:
    """Check if traveling between two cities in the given time is physically impossible.

    Uses a max speed of 900 km/h (approximate commercial flight speed) as the threshold.

    Args:
        city1: Name of the first city
        city2: Name of the second city
        time_diff_seconds: Time difference between transactions in seconds
        max_speed_kmh: Maximum realistic travel speed in km/h

    Returns:
        True if travel is impossible (fraud indicator)
    """
    coords1 = get_city_coordinates(city1)
    coords2 = get_city_coordinates(city2)

    if coords1 is None or coords2 is None:
        return False  # Can't determine if unknown cities

    if city1.lower() == city2.lower():
        return False  # Same city, no travel needed

    distance_km = haversine_distance(coords1[0], coords1[1], coords2[0], coords2[1])

    # Time needed at max speed (in seconds)
    time_needed_seconds = (distance_km / max_speed_kmh) * 3600

    return time_diff_seconds < time_needed_seconds
