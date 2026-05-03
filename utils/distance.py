"""
Distance calculation utilities for geographic coordinates.
Uses the Haversine formula to calculate distances between two points on Earth.
"""
import math
from typing import Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
    
    Returns:
        Distance between the two points in kilometers, rounded to 2 decimal places
    
    Example:
        >>> calculate_distance(-6.2088, 106.8456, -6.1751, 106.8650)
        4.32
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Calculate distance
    distance = R * c
    
    return round(distance, 2)


def calculate_distances_from_point(
    origin_lat: float,
    origin_lon: float,
    destinations: list[dict]
) -> dict[str, float]:
    """
    Calculate distances from a single origin point to multiple destinations.
    
    Args:
        origin_lat: Latitude of origin point
        origin_lon: Longitude of origin point
        destinations: List of dictionaries with 'id', 'latitude', and 'longitude' keys
    
    Returns:
        Dictionary mapping destination IDs to distances in kilometers
    
    Example:
        >>> destinations = [
        ...     {'id': 'centra1', 'latitude': -6.2088, 'longitude': 106.8456},
        ...     {'id': 'centra2', 'latitude': -6.1751, 'longitude': 106.8650}
        ... ]
        >>> calculate_distances_from_point(-6.2000, 106.8500, destinations)
        {'centra1': 1.23, 'centra2': 3.45}
    """
    distances = {}
    
    for dest in destinations:
        dest_id = dest.get('id') or dest.get('user_id') or dest.get('centra_id')
        dest_lat = dest.get('latitude')
        dest_lon = dest.get('longitude')
        
        if dest_id and dest_lat is not None and dest_lon is not None:
            distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
            distances[str(dest_id)] = distance
    
    return distances


def sort_by_distance(
    origin_lat: float,
    origin_lon: float,
    items: list[dict],
    latitude_key: str = 'latitude',
    longitude_key: str = 'longitude'
) -> list[Tuple[dict, float]]:
    """
    Sort a list of items by their distance from an origin point.
    
    Args:
        origin_lat: Latitude of origin point
        origin_lon: Longitude of origin point
        items: List of dictionaries containing location data
        latitude_key: Key name for latitude in the dictionaries (default: 'latitude')
        longitude_key: Key name for longitude in the dictionaries (default: 'longitude')
    
    Returns:
        List of tuples (item, distance) sorted by distance (closest first)
    
    Example:
        >>> items = [
        ...     {'name': 'A', 'latitude': -6.2088, 'longitude': 106.8456},
        ...     {'name': 'B', 'latitude': -6.1751, 'longitude': 106.8650}
        ... ]
        >>> sort_by_distance(-6.2000, 106.8500, items)
        [({'name': 'A', ...}, 1.23), ({'name': 'B', ...}, 3.45)]
    """
    items_with_distance = []
    
    for item in items:
        lat = item.get(latitude_key)
        lon = item.get(longitude_key)
        
        if lat is not None and lon is not None:
            distance = calculate_distance(origin_lat, origin_lon, lat, lon)
            items_with_distance.append((item, distance))
    
    # Sort by distance (ascending)
    items_with_distance.sort(key=lambda x: x[1])
    
    return items_with_distance


def get_closest_items(
    origin_lat: float,
    origin_lon: float,
    items: list[dict],
    limit: int = None,
    max_distance: float = None,
    latitude_key: str = 'latitude',
    longitude_key: str = 'longitude'
) -> list[Tuple[dict, float]]:
    """
    Get the closest items to an origin point, optionally limited by count or max distance.
    
    Args:
        origin_lat: Latitude of origin point
        origin_lon: Longitude of origin point
        items: List of dictionaries containing location data
        limit: Maximum number of items to return (optional)
        max_distance: Maximum distance in kilometers (optional)
        latitude_key: Key name for latitude in the dictionaries
        longitude_key: Key name for longitude in the dictionaries
    
    Returns:
        List of tuples (item, distance) sorted by distance, limited by count/distance
    """
    sorted_items = sort_by_distance(origin_lat, origin_lon, items, latitude_key, longitude_key)
    
    # Filter by max distance if specified
    if max_distance is not None:
        sorted_items = [(item, dist) for item, dist in sorted_items if dist <= max_distance]
    
    # Limit number of results if specified
    if limit is not None:
        sorted_items = sorted_items[:limit]
    
    return sorted_items
