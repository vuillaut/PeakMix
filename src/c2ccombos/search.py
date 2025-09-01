from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .client import C2CClient
from .geo import doc_point_xy, expand_bbox, mercator_point_distance_m
from .params import BaseSearchParams, RouteSearchParams, WaypointSearchParams


@dataclass
class NearbyMatch:
    route: Mapping[str, Any]
    waypoint: Mapping[str, Any]
    distance_m: float


class C2CSearch:
    """High-level search utilities built on top of C2CClient.

    Keep logic thin and generic, rely on params for filtering.
    """

    def __init__(self, client: Optional[C2CClient] = None) -> None:
        self.client = client or C2CClient()

    # Generic list methods
    def list_routes(self, params: Optional[BaseSearchParams] = None, **kwargs: Any) -> Dict[str, Any]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        return self.client.list_routes(**p)

    def list_waypoints(self, params: Optional[BaseSearchParams] = None, **kwargs: Any) -> Dict[str, Any]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        return self.client.list_waypoints(**p)

    # Core primitive: search within a bbox
    def routes_in_bbox(self, bbox: Tuple[float, float, float, float], params: Optional[RouteSearchParams] = None, **kwargs: Any) -> List[Mapping[str, Any]]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        p["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        res = self.list_routes(**p)
        return list(res.get("documents", []))

    def waypoints_in_bbox(self, bbox: Tuple[float, float, float, float], params: Optional[WaypointSearchParams] = None, **kwargs: Any) -> List[Mapping[str, Any]]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        p["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        res = self.list_waypoints(**p)
        return list(res.get("documents", []))

    # Pagination helpers
    def _paginate(
        self,
        endpoint: str,
        page_size: int = 100,
        max_items: Optional[int] = None,
        **params: Any,
    ) -> List[Mapping[str, Any]]:
        """Iterate endpoint with offset/limit until exhausted or max_items reached."""
        items: List[Mapping[str, Any]] = []
        offset = int(params.get("offset", 0) or 0)
        seen = 0
        while True:
            page_params = dict(params)
            page_params.update({"limit": page_size, "offset": offset})
            if endpoint == "routes":
                res = self.client.list_routes(**page_params)
            elif endpoint == "waypoints":
                res = self.client.list_waypoints(**page_params)
            else:
                res = self.client.get(endpoint, params=page_params)
            docs = list(res.get("documents", []) or [])
            if not docs:
                break
            for d in docs:
                items.append(d)
                seen += 1
                if max_items is not None and seen >= max_items:
                    return items
            offset += len(docs)
            # Stop if returned fewer than requested, assuming end
            if len(docs) < page_size:
                break
        return items

    def routes_in_bbox_all(
        self,
        bbox: Tuple[float, float, float, float],
        *,
        page_size: int = 100,
        max_items: Optional[int] = None,
        params: Optional[RouteSearchParams] = None,
        **kwargs: Any,
    ) -> List[Mapping[str, Any]]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        p["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        return self._paginate("routes", page_size=page_size, max_items=max_items, **p)

    def waypoints_in_bbox_all(
        self,
        bbox: Tuple[float, float, float, float],
        *,
        page_size: int = 100,
        max_items: Optional[int] = None,
        params: Optional[WaypointSearchParams] = None,
        **kwargs: Any,
    ) -> List[Mapping[str, Any]]:
        p = params.to_query_params() if isinstance(params, BaseSearchParams) else {}
        p.update(kwargs)
        p["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        return self._paginate("waypoints", page_size=page_size, max_items=max_items, **p)

    # Higher-level: find routes near waypoints
    def routes_near_waypoints(
        self,
        waypoints: Iterable[Mapping[str, Any]],
        max_distance_m: float = 2000.0,
        route_params: Optional[Mapping[str, Any]] = None,
        *,
        route_page_size: int = 100,
        route_max_items: Optional[int] = None,
    ) -> List[NearbyMatch]:
        """Return route-waypoint pairs within a distance threshold.

        Strategy:
        - Compute padded bbox around all waypoints
        - Query routes once per bbox
        - Compute precise distances and filter
        """
        wps = list(waypoints)
        if not wps:
            return []

        # Compute aggregate bbox from waypoint points/bboxes
        xs: List[float] = []
        ys: List[float] = []
        for wp in wps:
            pt = doc_point_xy(wp)
            if pt:
                xs.append(pt[0])
                ys.append(pt[1])
            else:
                bbox = wp.get("bbox")
                if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                    xs.extend([float(bbox[0]), float(bbox[2])])
                    ys.extend([float(bbox[1]), float(bbox[3])])
        if not xs or not ys:
            return []

        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        pad = max(max_distance_m, 1000.0)
        bbox = expand_bbox(minx, miny, maxx, maxy, pad)

        # Fetch routes with pagination so we don't limit to API default (30)
        if isinstance(route_params, BaseSearchParams):
            rparams_obj = route_params
        elif isinstance(route_params, Mapping):
            # keep backward compat with dict
            rparams_obj = None
        else:
            rparams_obj = None

        routes = self.routes_in_bbox_all(
            bbox,
            page_size=route_page_size,
            max_items=route_max_items,
            params=rparams_obj,  # may be None
            **(route_params if isinstance(route_params, Mapping) else {}),
        )

        matches: List[NearbyMatch] = []
        for route in routes:
            rpt = doc_point_xy(route)
            if not rpt:
                continue
            for wp in wps:
                wpt = doc_point_xy(wp)
                if not wpt:
                    continue
                d = mercator_point_distance_m(rpt, wpt)
                if d <= max_distance_m:
                    matches.append(NearbyMatch(route=route, waypoint=wp, distance_m=d))

        # Sort by distance for convenience
        matches.sort(key=lambda m: m.distance_m)
        return matches
