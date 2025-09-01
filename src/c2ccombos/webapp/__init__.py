from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from typing import Any, Dict

from ..search import C2CSearch
from ..geo import lonlat_to_webmercator, bbox_around_xy, doc_point_lonlat
from ..utils import doc_url
from ..params import WaypointSearchParams, RouteSearchParams


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    search = C2CSearch()

    @app.get("/ui")
    def ui() -> str:
        return render_template("index.html")

    @app.get("/api/search")
    def api_search():
        try:
            lon = float(request.args.get("lon", "0"))
            lat = float(request.args.get("lat", "0"))
            box = float(request.args.get("box", "20000"))
            max_distance = float(request.args.get("max_distance", "2000"))
            act = request.args.get("act", "rock_climbing")
            wtyp = request.args.get("wtyp", "paragliding_takeoff")
            wfac = request.args.get("wfac")  # optional comma-separated orientations
            fratmin = request.args.get("fratmin") or None
            fratmax = request.args.get("fratmax") or None
        except Exception:
            return jsonify({"error": "invalid parameters"}), 400

        x, y = lonlat_to_webmercator(lon, lat)
        bbox = bbox_around_xy(x, y, box)

        # Fetch takeoffs
        wp_params = WaypointSearchParams(
            act=act,
            wtyp=wtyp,
            orientations=wfac,
            fields=[
                "document_id",
                "locales",
                "geometry",
                "bbox",
                "orientations",
                "wfac",
            ],
            lang=request.args.get("lang"),
        )
        waypoints = search.waypoints_in_bbox_all(
            bbox, page_size=200, max_items=2000, params=wp_params
        )

        # Fetch routes near takeoffs
        route_params = RouteSearchParams(
            act=act,
            rock_free_rating=(fratmin, fratmax) if (fratmin or fratmax) else None,
            fields=[
                "document_id",
                "locales",
                "geometry",
                "bbox",
                "rock_free_rating",
                "rock_required_rating",
                "global_rating",
                "orientations",
            ],
            lang=request.args.get("lang"),
        )
        matches = search.routes_near_waypoints(
            waypoints,
            max_distance_m=max_distance,
            route_params=route_params,
            route_page_size=400,
            route_max_items=4000,
        )

        # Build GeoJSON-like output for map
        def feature_from_doc(doc: Dict[str, Any], dtype: str) -> Dict[str, Any]:
            ll = doc_point_lonlat(doc)
            if not ll:
                return {}
            url = doc_url(doc)
            # Enrich properties with ratings and orientations when available
            props: Dict[str, Any] = {
                "id": doc.get("document_id"),
                "type": dtype,
                "title": (
                    doc.get("locales", [{}])[0].get("title")
                    or doc.get("name")
                    or str(doc.get("document_id"))
                ),
                "url": url,
            }
            if dtype == "route":
                props.update(
                    {
                        "free": doc.get("rock_free_rating") or doc.get("global_rating"),
                        "oblig": doc.get("rock_required_rating"),
                        "global": doc.get("global_rating"),
                        "orientations": doc.get("orientations"),
                    }
                )
            else:
                # Waypoint: prefer explicit orientations; keep simple fallbacks if API differs
                props.update({
                    "orientations": doc.get("orientations")
                        or doc.get("fac")
                        or doc.get("orientation")
                        or doc.get("wfac")
                })
            return {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [ll[0], ll[1]]},
                "properties": props,
            }

        takeoff_features = [
            f for f in (feature_from_doc(wp, "waypoint") for wp in waypoints) if f
        ]
        route_features = [
            f for f in (feature_from_doc(m.route, "route") for m in matches) if f
        ]

        return jsonify(
            {
                "takeoffs": takeoff_features,
                "routes": route_features,
                "counts": {"takeoffs": len(takeoff_features), "routes": len(route_features)},
            }
        )

    return app
