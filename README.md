# c2ccombos

Camp to Camp route and waypoint search utilities.

<img width="1915" height="928" alt="c2ccombos" src="https://github.com/user-attachments/assets/f4992c0f-0cb1-4b83-a6f3-5a7efb83fff5" />



## Install

```bash
pip install -e .
```

Requires Python 3.9+.

## Quick start

```python
from c2ccombos import C2CSearch, doc_url

search = C2CSearch()

# Find waypoints (e.g., paragliding takeoffs) in a bbox (EPSG:3857 meters)
# Use the _all variant to fetch beyond API default (30), with configurable page size and cap
waypoints = search.waypoints_in_bbox_all(
  (480157, 5566851, 867311, 5915568),
  act="mountain_climbing",
  wtyp="paragliding_takeoff",
  page_size=200,
  max_items=2000,
)

# Find routes near those waypoints within 2 km
matches = search.routes_near_waypoints(
    waypoints,
    max_distance_m=2000,
  route_params={"act": "mountain_climbing"},
  route_page_size=200,
  route_max_items=5000,
)

for m in matches[:10]:
    rname = m.route.get("locales", [{}])[0].get("title") or m.route.get("name")
    wname = m.waypoint.get("locales", [{}])[0].get("title") or m.waypoint.get("name")
  print(f"{m.distance_m:.0f} m: {rname} near {wname}  {doc_url(m.route)}")
```

## CLI usage

After installing in editable mode, a `c2ccombos` command is available.

Search near a GPS location (lon, lat) with a square box of given size in meters (auto-computes bbox in EPSG:3857):

```bash
c2ccombos near 6.866 45.922 20000 \
  --act mountain_climbing \
  --wtyp paragliding_takeoff \
  --max-distance 2000 \
  --route-page-size 200 --route-max-items 5000 \
  --wp-page-size 200 --wp-max-items 2000 \
  --lang fr --fields document_id,locales,geometry --orderby elevation_max --order desc \
  --extra prom=500
```

This prints waypoint count, matches, and up to 50 closest matches with route URLs.

## Run the Web UI locally

Option A — Serve backend and UI together (simplest):

```bash
# 1) Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 2) Install
pip install -e .

# 3) Start the Web UI
c2ccombos-web
# It serves the UI at http://127.0.0.1:8000/ui
```

If port 8000 is busy:

```bash
PORT=8001 c2ccombos-web
```

Open http://127.0.0.1:8000/ui (or the port you chose) in your browser.

Option B — Serve the static page and point it to your local API:

```bash
# In one terminal, run the backend (as above)
c2ccombos-web

# In another terminal, serve the static UI from docs/
python -m http.server 8080 -d docs
# Open http://127.0.0.1:8080/?api=http://127.0.0.1:8000
```

Note: The search needs the backend running; the static page alone won’t fetch results.

Tips:

- Override address: `c2ccombos-web --host 0.0.0.0 --port 8001`
- If `c2ccombos-web` isn’t found after install, refresh your shell (`hash -r` in zsh) or open a new terminal.

## Design

- Core HTTP client (`C2CClient`):
  - Generic GET with base URL, timeouts, headers.
  - Convenience `list_routes` and `list_waypoints` keep the client minimal.
- Models: thin, optional pydantic models for common shapes. The search layer works on dicts to avoid over-constraining.
- Geo helpers: small functions for bbox padding, point extraction from GeoJSON-like geometries, and distance approximation in Web Mercator.
  - Includes `doc_url(doc)` utility to link to the CampToCamp website.
- High-level `C2CSearch`:
  - `routes_in_bbox`, `waypoints_in_bbox` simple wrappers.
  - `routes_in_bbox_all`, `waypoints_in_bbox_all` use pagination.
  - `routes_near_waypoints` composes primitives and returns sorted matches with distances; supports route pagination parameters.
  - Params builders (`RouteSearchParams`, `WaypointSearchParams`) support common options and arbitrary `extras` for full API coverage and future UI forms.

## API notes

- All bbox coordinates are in EPSG:3857 meters, identical order to the API: `minx,miny,maxx,maxy`.
- Responses are returned as raw dicts from the API to maximize flexibility.
- Distance is Euclidean in Web Mercator, which is good enough for small ranges (1–5 km). For larger distances, consider geodesic calculations.

### Search filters coverage

`RouteSearchParams` and `WaypointSearchParams` now cover the official v6 API search filters and use the public query keys under the hood. A few examples:

- Routes:
  - Activities: `act=["rock_climbing","mountain_climbing"]`
  - Elevation: `elevation=(1000, 3500)` → `ele=1000,3500`
  - Orientations: `orientations=["W","S"]` → `fac=W,S`
  - Types: `route_types=["rock_climbing"]` → `rtyp=rock_climbing`
  - Ratings: `global_rating=("AD","D+")` → `grat=AD,D+`, `rock_free_rating=("6a","6c+")` → `frat=6a,6c+`, `rock_required_rating=("5c", None)` → `rrat=5c,`

- Waypoints:
  - Waypoint type: `wtyp=["paragliding_takeoff","summit"]`
  - Elevation/prominence: `elevation=("1000","2000")` → `walt=1000,2000`, `prominence=(300,None)` → `prom=300,`
  - Orientations: `orientations=["N"]` → `wfac=N`
  - Paragliding/climbing ratings: `paragliding_rating=("2","4")` → `pgrat=2,4`, `climbing_rating_max=("6a","7a")` → `tmaxr=6a,7a`

All numeric or enum ranges accept either a pre-formatted string "min,max" or a tuple `(min, max)`; open bounds are supported using `None`.

## Extending

- Add more helpers in `search.py` that compose the core:
  - `waypoints_near_route_centers`, `clusters_by_takeoff`, pagination helpers, etc.
- If you prefer typed models, adapt `models.py` and wrap/validate the `documents` items.

## Minimal CLI example

```python
from c2ccombos import C2CSearch

if __name__ == "__main__":
    s = C2CSearch()
    wps = s.waypoints_in_bbox((480157,5566851,867311,5915568), act="mountain_climbing", wtyp="paragliding_takeoff")
    matches = s.routes_near_waypoints(wps, 2000, route_params={"act":"mountain_climbing"})
    for m in matches[:20]:
        print(m.distance_m, m.route.get("document_id"), m.waypoint.get("document_id"))
```
