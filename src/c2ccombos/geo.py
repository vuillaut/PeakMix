from __future__ import annotations

import math
import json
from typing import Any, Mapping, Optional

# Minimal geospatial helpers kept internal & dependency-free.


def mercator_point_distance_m(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Euclidean distance in EPSG:3857 (meters-like).

    For small distances, Euclidean distance in Web Mercator is acceptable.
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.hypot(dx, dy)


def expand_bbox(minx: float, miny: float, maxx: float, maxy: float, pad_m: float) -> tuple[float, float, float, float]:
    return (minx - pad_m, miny - pad_m, maxx + pad_m, maxy + pad_m)


def point_in_bbox(x: float, y: float, bbox: tuple[float, float, float, float]) -> bool:
    minx, miny, maxx, maxy = bbox
    return (minx <= x <= maxx) and (miny <= y <= maxy)


# Projections (EPSG:4326 -> EPSG:3857)
_R = 6378137.0  # WGS84 spheroid radius


def lonlat_to_webmercator(lon: float, lat: float) -> tuple[float, float]:
    """Convert longitude/latitude in degrees to Web Mercator meters (EPSG:3857)."""
    # Clamp latitude to Mercator projection bounds
    max_lat = 85.05112878
    lat = max(min(lat, max_lat), -max_lat)
    x = math.radians(lon) * _R
    y = math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0)) * _R
    return x, y


def webmercator_to_lonlat(x: float, y: float) -> tuple[float, float]:
    """Convert Web Mercator meters (EPSG:3857) to lon/lat degrees (EPSG:4326)."""
    lon = math.degrees(x / _R)
    lat = math.degrees(2.0 * math.atan(math.exp(y / _R)) - math.pi / 2.0)
    return lon, lat


def bbox_around_xy(center_x: float, center_y: float, box_size_m: float) -> tuple[float, float, float, float]:
    """Return bbox of width=height=box_size_m centered on (x,y) in EPSG:3857."""
    half = box_size_m / 2.0
    return (center_x - half, center_y - half, center_x + half, center_y + half)


def first_point_xy_from_geometry(geometry: Mapping[str, Any]) -> Optional[tuple[float, float]]:
    """Return a representative XY point from a GeoJSON-like geometry.

    Supports Point, LineString, Polygon and Multi* by picking the first coordinate.
    Coordinates expected as [x, y, ...] in EPSG:3857.
    """
    try:
        # C2C often provides { 'geom': '{"type":"Point","coordinates":[x,y]}' }
        if "geom" in geometry and isinstance(geometry["geom"], str):
            try:
                parsed = json.loads(geometry["geom"])  # may raise
                return first_point_xy_from_geometry(parsed)  # recurse on parsed GeoJSON
            except Exception:
                return None

        gtype = geometry.get("type")
        coords = geometry.get("coordinates")
    except AttributeError:
        return None

    if not coords:
        return None

    if gtype == "Point":
        x, y = coords[0], coords[1]
        return float(x), float(y)

    # For LineString, Polygon, Multi*, drill down to first [x, y]
    def drill(c: Any) -> Optional[tuple[float, float]]:
        if not isinstance(c, (list, tuple)) or not c:
            return None
        if isinstance(c[0], (int, float)) and len(c) >= 2:
            return float(c[0]), float(c[1])
        return drill(c[0])

    return drill(coords)


def doc_point_xy(doc: Mapping[str, Any]) -> Optional[tuple[float, float]]:
    """Best-effort extraction of a representative XY point from a C2C document.

    Attempts, in order:
    - geometry.coordinates (GeoJSON-like)
    - bbox center if bbox present as [minx, miny, maxx, maxy]
    """
    geom = doc.get("geometry") if isinstance(doc, Mapping) else None
    pt = first_point_xy_from_geometry(geom) if geom else None
    if pt is not None:
        return pt
    bbox = doc.get("bbox") if isinstance(doc, Mapping) else None
    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
        minx, miny, maxx, maxy = bbox
        return (float(minx) + float(maxx)) / 2.0, (float(miny) + float(maxy)) / 2.0
    return None


def doc_point_lonlat(doc: Mapping[str, Any]) -> Optional[tuple[float, float]]:
    """Extract representative lon/lat for a C2C document if possible."""
    xy = doc_point_xy(doc)
    if xy is None:
        return None
    return webmercator_to_lonlat(xy[0], xy[1])
