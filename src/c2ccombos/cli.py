from __future__ import annotations

import argparse
from typing import Optional

from .search import C2CSearch
from .geo import lonlat_to_webmercator, bbox_around_xy
from .utils import doc_url
from .params import WaypointSearchParams, RouteSearchParams


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="c2ccombos",
        description="Find C2C routes near paragliding takeoffs or a GPS location.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("near", help="Search routes near a GPS point")
    s.add_argument("lon", type=float, help="Longitude in degrees (EPSG:4326)")
    s.add_argument("lat", type=float, help="Latitude in degrees (EPSG:4326)")
    s.add_argument("box", type=float, help="Box size in meters (width=height)")
    s.add_argument("--act", default="mountain_climbing", help="Activity filter for routes and waypoints (comma-separated for multiple)")
    s.add_argument("--wtyp", default="paragliding_takeoff", help="Waypoint type to consider (comma-separated for multiple)")
    s.add_argument("--max-distance", type=float, default=2000.0, help="Max distance in meters to match routes to waypoints")
    s.add_argument("--route-page-size", type=int, default=200)
    s.add_argument("--route-max-items", type=int, default=5000)
    s.add_argument("--wp-page-size", type=int, default=200)
    s.add_argument("--wp-max-items", type=int, default=2000)
    # Advanced search options
    s.add_argument("--lang", default=None, help="Preferred language code for localized fields")
    s.add_argument("--fields", default=None, help="Comma-separated list of fields to return")
    s.add_argument("--orderby", default=None, help="Field to order by")
    s.add_argument("--order", default=None, help="asc or desc")
    s.add_argument(
        "--extra",
        action="append",
        default=[],
        help="Additional key=value pairs passed directly to the API (can be repeated)",
    )
    return p


def cmd_near(args: argparse.Namespace) -> int:
    x, y = lonlat_to_webmercator(args.lon, args.lat)
    bbox = bbox_around_xy(x, y, args.box)

    s = C2CSearch()

    # Build typed params with extras for both waypoints and routes
    def parse_csv(v: str | None):
        if not v:
            return None
        return [p.strip() for p in v.split(",") if p.strip()]

    def parse_extras(items: list[str]):
        extras: dict[str, str] = {}
        for entry in items or []:
            if "=" in entry:
                k, v = entry.split("=", 1)
                extras[k.strip()] = v.strip()
        return extras

    # Default fields include geometry + ratings for difficulty display if user didn't pass --fields
    default_fields = ["document_id", "locales", "geometry", "rock_free_rating", "rock_required_rating", "global_rating"]
    common_kwargs = {
        "lang": args.lang,
        "fields": parse_csv(args.fields) if args.fields else default_fields,
        "orderby": args.orderby,
        "order": args.order,
    }
    wp_params = WaypointSearchParams(
        **common_kwargs,
        wtyp=parse_csv(args.wtyp) or args.wtyp,
        act=parse_csv(args.act) or args.act,
        extras=parse_extras(args.extra),
    )

    waypoints = s.waypoints_in_bbox_all(
        bbox,
        page_size=args.wp_page_size,
        max_items=args.wp_max_items,
        params=wp_params,
    )
    print(f"Waypoints fetched: {len(waypoints)}")

    route_params = RouteSearchParams(
        **common_kwargs,
        act=parse_csv(args.act) or args.act,
        extras=parse_extras(args.extra),
    )
    matches = s.routes_near_waypoints(
        waypoints,
        max_distance_m=args.max_distance,
        route_params=route_params,
        route_page_size=args.route_page_size,
        route_max_items=args.route_max_items,
    )
    print(f"Matches found: {len(matches)} (<= {args.max_distance:.0f} m)\n")

    # Group matches by waypoint (décollage)
    from collections import defaultdict

    def title_of(doc: dict) -> str:
        return (doc.get("locales", [{}])[0].get("title") or doc.get("name") or str(doc.get("document_id")))

    grouped = defaultdict(list)
    for m in matches:
        wid = m.waypoint.get("document_id") or m.waypoint.get("id")
        if wid is None:
            continue
        grouped[wid].append(m)

    # Sort takeoffs by number of routes desc, then by name
    waypoint_order = sorted(grouped.items(), key=lambda kv: (-len(kv[1]), title_of(kv[1][0].waypoint)))

    def truncate(text: str, width: int) -> str:
        return text if len(text) <= width else text[: max(0, width - 1)] + "…"

    def route_difficulty(r: dict) -> str:
        free = r.get("rock_free_rating") or r.get("global_rating")
        obl = r.get("rock_required_rating")
        if free and obl:
            return f"{free} (obl {obl})"
        if free:
            return str(free)
        return "-"

    for wid, mlist in waypoint_order:
        wp_doc = mlist[0].waypoint
        wtitle = title_of(wp_doc)
        wurl = doc_url(wp_doc) or ""
        print("=" * 80)
        print(f"Décollage: {wtitle}")
        if wurl:
            print(f"URL       : {wurl}")
        print(f"Routes    : {len(mlist)} within {int(args.max_distance)} m\n")

        # Sort routes by distance
        mlist_sorted = sorted(mlist, key=lambda x: x.distance_m)

        # Table header
        route_col_w = 50
        diff_col_w = 12
        print(f"{'Dist (m)':>9} | {'Diff':<{diff_col_w}} | {'Route':<{route_col_w}} | URL")
        print("-" * 80)
        for m in mlist_sorted:
            rname = title_of(m.route)
            rurl = doc_url(m.route) or ""
            diff = route_difficulty(m.route)
            print(f"{int(round(m.distance_m)):>9} | {truncate(diff, diff_col_w):<{diff_col_w}} | {truncate(rname, route_col_w):<{route_col_w}} | {rurl}")
        print()

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    if args.cmd == "near":
        return cmd_near(args)
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
