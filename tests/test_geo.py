from c2ccombos.geo import mercator_point_distance_m, expand_bbox, point_in_bbox, first_point_xy_from_geometry, doc_point_xy


def test_distance_and_bbox():
    assert mercator_point_distance_m((0, 0), (3, 4)) == 5
    bbox = expand_bbox(0, 0, 10, 10, 2)
    assert bbox == (-2, -2, 12, 12)
    assert point_in_bbox(5, 5, bbox)


def test_point_extraction():
    pt = first_point_xy_from_geometry({"type": "Point", "coordinates": [1, 2]})
    assert pt == (1.0, 2.0)
    pt2 = first_point_xy_from_geometry({"type": "Polygon", "coordinates": [[[1, 2], [3, 4], [1, 2]]]})
    assert pt2 == (1.0, 2.0)

    doc = {"geometry": {"type": "LineString", "coordinates": [[5, 6], [7, 8]]}}
    assert doc_point_xy(doc) == (5.0, 6.0)
    assert doc_point_xy({"bbox": [0, 0, 10, 10]}) == (5.0, 5.0)
