from c2ccombos.geo import doc_point_xy


def test_c2c_geometry_geom_string():
    doc = {"geometry": {"version": 1, "geom": '{"type": "Point", "coordinates": [703332.906594, 5645975.4795]}'}}
    pt = doc_point_xy(doc)
    assert pt == (703332.906594, 5645975.4795)
