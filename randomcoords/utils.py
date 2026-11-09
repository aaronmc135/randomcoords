from .generators import Coordinates

def to_google_maps_link(coords: Coordinates) -> str:
    """Return a Google Maps URL for a (long, lat) point."""
    lon, lat = coords
    # Google expects lat,long. Fixed decimals also prevent scientific notation like 1e-05.
    return f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{lon:.6f}"
