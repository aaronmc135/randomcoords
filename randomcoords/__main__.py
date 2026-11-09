import argparse
import csv
import json
import os
import random
import sys
from typing import List, Optional

from .generators import CircularArea, Coordinates, RandomCoordinateGenerator
from .utils import to_google_maps_link

FORMATS = ["text", "link", "csv", "json", "geojson"]
CSV_COLUMNS = ["lat", "lon", "link", "json"]
DEFAULT_CSV_COLUMNS = ["lat", "lon"]
DECIMALS = 6


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def latitude(value: str) -> float:
    number = float(value)
    if not -90 <= number <= 90:
        raise argparse.ArgumentTypeError("must be between -90 and 90")
    return number


def longitude(value: str) -> float:
    number = float(value)
    if not -180 <= number <= 180:
        raise argparse.ArgumentTypeError("must be between -180 and 180")
    return number


def non_negative_float(value: str) -> float:
    number = float(value)
    if not number >= 0:
        raise argparse.ArgumentTypeError("must be 0 or greater")
    return number


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--count", type=positive_int, default=1, help="number of points (default: 1)")
    common.add_argument("--seed", type=int, help="seed for reproducible results")
    common.add_argument("--format", choices=FORMATS, default="text", help="output format (default: text)")
    common.add_argument(
        "--columns",
        nargs="+",
        choices=CSV_COLUMNS,
        help="CSV columns, in output order (default: lat lon)",
    )

    parser = argparse.ArgumentParser(prog="randomcoords", description="Generate random coordinates.")
    subparsers = parser.add_subparsers(dest="area", required=True)

    subparsers.add_parser("globe", parents=[common], help="anywhere on the globe")

    circle = subparsers.add_parser("circle", parents=[common], help="within a radius of a center point")
    circle.add_argument("--lat", type=latitude, required=True, help="latitude of the center")
    circle.add_argument("--lon", type=longitude, required=True, help="longitude of the center")
    circle.add_argument("--radius", type=non_negative_float, required=True, help="radius in miles")

    return parser


def build_generator(args: argparse.Namespace) -> RandomCoordinateGenerator:
    if args.area == "circle":
        return CircularArea((args.lon, args.lat), args.radius)
    return RandomCoordinateGenerator()


def as_lat_lon_dict(point: Coordinates) -> dict:
    lon, lat = point
    return {"lat": round(lat, DECIMALS), "lon": round(lon, DECIMALS)}


def csv_cell(point: Coordinates, column: str) -> str:
    lon, lat = point
    if column == "lat":
        return f"{lat:.{DECIMALS}f}"
    if column == "lon":
        return f"{lon:.{DECIMALS}f}"
    if column == "link":
        return to_google_maps_link(point)
    return json.dumps(as_lat_lon_dict(point))


def write_csv(points: List[Coordinates], columns: List[str]) -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(columns)
    for point in points:
        writer.writerow([csv_cell(point, column) for column in columns])


def write_geojson(points: List[Coordinates]) -> None:
    features = [
        {
            "type": "Feature",
            # GeoJSON requires long, lat order.
            "geometry": {"type": "Point", "coordinates": [round(lon, DECIMALS), round(lat, DECIMALS)]},
            "properties": {},
        }
        for lon, lat in points
    ]
    print(json.dumps({"type": "FeatureCollection", "features": features}, indent=2))


def write_points(points: List[Coordinates], args: argparse.Namespace) -> None:
    if args.format == "csv":
        write_csv(points, args.columns or DEFAULT_CSV_COLUMNS)
    elif args.format == "json":
        print(json.dumps([as_lat_lon_dict(point) for point in points], indent=2))
    elif args.format == "geojson":
        write_geojson(points)
    elif args.format == "link":
        for point in points:
            print(to_google_maps_link(point))
    else:
        for lon, lat in points:
            print(f"{lat:.{DECIMALS}f}, {lon:.{DECIMALS}f}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.columns is not None and args.format != "csv":
        parser.error("--columns can only be used with --format csv")

    if args.seed is not None:
        random.seed(args.seed)

    generator = build_generator(args)
    points = [generator.generate_random_coords() for _ in range(args.count)]

    try:
        write_points(points, args)
        sys.stdout.flush()
    except BrokenPipeError:
        # The reader closed early, as with `| head`. Stop quietly without a traceback at exit.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0


if __name__ == "__main__":
    sys.exit(main())
