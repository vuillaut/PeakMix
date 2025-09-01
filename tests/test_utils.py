from c2ccombos.utils import doc_url


def test_doc_url_routes_and_waypoints():
    r = {"type": "r", "document_id": 123}
    w = {"type": "w", "document_id": 456}
    assert doc_url(r) == "https://www.camptocamp.org/routes/123"
    assert doc_url(w) == "https://www.camptocamp.org/waypoints/456"

    # Heuristic when type missing
    r2 = {"document_id": 789, "activities": ["mountain_climbing"]}
    w2 = {"document_id": 999, "waypoint_type": "paragliding_takeoff"}
    assert doc_url(r2) == "https://www.camptocamp.org/routes/789"
    assert doc_url(w2) == "https://www.camptocamp.org/waypoints/999"
