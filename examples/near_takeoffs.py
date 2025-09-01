from c2ccombos import C2CSearch, doc_url


def main():
    s = C2CSearch()
    bbox = (480157, 5566851, 867311, 5915568)

    # Fetch many takeoff waypoints
    wps = s.waypoints_in_bbox_all(
        bbox,
        page_size=200,
        max_items=2000,
        act="mountain_climbing",
        wtyp="paragliding_takeoff",
    )
    print(f"Fetched {len(wps)} takeoff waypoints")

    matches = s.routes_near_waypoints(
        wps,
        max_distance_m=2000,
        route_params={"act": "mountain_climbing"},
        route_page_size=200,
        route_max_items=5000,
    )
    print(f"Found {len(matches)} route-waypoint matches within 2km")

    for m in matches[:20]:
        rname = (m.route.get("locales", [{}])[0].get("title") or m.route.get("name") or str(m.route.get("document_id")))
        wname = (m.waypoint.get("locales", [{}])[0].get("title") or m.waypoint.get("name") or str(m.waypoint.get("document_id")))
        url = doc_url(m.route) or ""
        print(f"{m.distance_m:.0f} m: {rname} near {wname}  {url}")


if __name__ == "__main__":
    main()
