import math
import random
from typing import Tuple

Coordinates = Tuple[float, float] # (Long, Lat)

EARTH_RADIUS_MILES = 3958.8

class RandomCoordinateGenerator:
    def generate_random_coords(self) -> Coordinates:
        """Return a point uniformly distributed over the whole globe."""
        lon = random.uniform(-180, 180)
        # Taking the arcsine of a uniform value stops points clustering at the poles.
        lat = math.degrees(math.asin(random.uniform(-1, 1)))
        return (lon, lat)

class CircularArea(RandomCoordinateGenerator):
    def __init__(self, center: Coordinates, radius: float):
        self.center = center
        self.radius = radius # Miles along the Earth's surface

    def generate_random_coords(self) -> Coordinates:
        """Return a point uniformly distributed within the radius of the center."""
        center_lon = math.radians(self.center[0])
        center_lat = math.radians(self.center[1])
        max_angle = min(self.radius / EARTH_RADIUS_MILES, math.pi)

        # The square root spreads points evenly by area instead of bunching them at the center.
        angle = 2 * math.asin(math.sqrt(random.random()) * math.sin(max_angle / 2))
        bearing = random.uniform(0, 2 * math.pi)

        # Find the point at that distance and bearing from the center.
        sin_lat = (
            math.sin(center_lat) * math.cos(angle)
            + math.cos(center_lat) * math.sin(angle) * math.cos(bearing)
        )
        sin_lat = max(-1.0, min(1.0, sin_lat)) # Guard against floating-point rounding
        lat = math.asin(sin_lat)
        lon = center_lon + math.atan2(
            math.sin(bearing) * math.sin(angle) * math.cos(center_lat),
            math.cos(angle) - math.sin(center_lat) * sin_lat,
        )

        # Wrap longitude back into range in case the area crosses the antimeridian.
        lon_degrees = (math.degrees(lon) + 180) % 360 - 180
        return (lon_degrees, math.degrees(lat))
