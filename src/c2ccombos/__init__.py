"""c2ccombos: Camp to Camp route and waypoint search utilities.

Public API:
- C2CClient: low-level HTTP client for the C2C API
- search: high-level search helpers
- models: typed models for routes and waypoints
- geo: minimal geospatial helpers
"""

from .client import C2CClient
from .search import C2CSearch
from .utils import doc_url
from .params import BaseSearchParams, RouteSearchParams, WaypointSearchParams
from . import models
from . import geo

__all__ = [
    "C2CClient",
    "C2CSearch",
    "models",
    "geo",
    "doc_url",
    "BaseSearchParams",
    "RouteSearchParams",
    "WaypointSearchParams",
]
