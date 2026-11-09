# randomcoords

Generate random coordinates anywhere on Earth, or within a radius of a point.

Points are spread evenly by surface area, so they don't cluster near the poles or bunch up at the center of a circle. There are no dependencies beyond the Python standard library.

## Usage

Run it from the repository root with Python 3.8 or later:

```bash
# Anywhere on the globe
python3 -m randomcoords globe

# Within 25 miles of Washington, DC
python3 -m randomcoords circle --lat 38.9072 --lon -77.0369 --radius 25
```

Output is `lat, lon`:

```text
38.822737, -77.378876
```

### Options

| Option | Description |
|---|---|
| `--count N` | Number of points (default: 1) |
| `--seed N` | Seed for reproducible results |
| `--format F` | `text` (default), `link`, `csv`, `json` or `geojson` |
| `--columns ...` | CSV columns in output order, from `lat`, `lon`, `link` and `json` (default: `lat lon`) |

`circle` also requires `--lat` and `--lon` for the center, and `--radius` in miles.

### Examples

```bash
# Google Maps links
python3 -m randomcoords globe --count 3 --format link

# The same points on every run
python3 -m randomcoords globe --count 10 --seed 42

# A CSV with custom columns
python3 -m randomcoords globe --count 100 --format csv --columns lat lon link > points.csv

# GeoJSON, which can be viewed at geojson.io or in QGIS
python3 -m randomcoords circle --lat 38.9072 --lon -77.0369 --radius 25 --count 50 --format geojson
```

## As a library

```python
from randomcoords.generators import CircularArea, RandomCoordinateGenerator
from randomcoords.utils import to_google_maps_link

lon, lat = RandomCoordinateGenerator().generate_random_coords()

dc = CircularArea((-77.0369, 38.9072), 25)
print(to_google_maps_link(dc.generate_random_coords()))
```

In Python, coordinates are `(lon, lat)` tuples, matching x, y order. The CLI's text, CSV and JSON output uses lat, lon, while GeoJSON uses lon, lat as its format requires.

## How it works

**Globe:** longitude is uniform from -180 to 180. Latitude is `asin(u)` for a uniform `u` from -1 to 1. Picking latitude uniformly in degrees would crowd points near the poles, where circles of latitude are shorter. Using `asin` matches Archimedes' hat-box theorem: equal slices of height along the Earth's axis have equal surface area. See [Sphere Point Picking](https://mathworld.wolfram.com/SpherePointPicking.html) on MathWorld.

**Circle:** the distance from the center is measured along the Earth's surface. It's drawn so that points are spread evenly by area rather than bunched at the center, and the bearing is uniform. The result is then projected from the center. This works near the poles and across the antimeridian.

## Limitations

- The Earth is treated as a sphere with a radius of 3,958.8 miles, so distances can be off by up to about 0.5%.
- The radius is always in miles.
- Seeded results come from Python's `random` module. They can differ in other implementations, and may change between Python versions.
- Not for anything security-sensitive. Use the `secrets` module for that.

## Credits

Written by [Claude](https://claude.com/claude-code), Anthropic's AI model, working with [@aaronmc135](https://github.com/aaronmc135).
