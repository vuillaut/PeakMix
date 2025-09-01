from c2ccombos.params import RouteSearchParams, WaypointSearchParams


def test_route_params_to_query():
    p = RouteSearchParams(
        q="alps",
        lang="fr",
        bbox=(0, 1, 2, 3),
        fields=["a", "b"],
        orderby="elevation_max",
        order="desc",
        limit=50,
        offset=10,
        act=["rock_climbing", "mountain_climbing"],
        waypoints=[123, 456],
        users="789",
        elevation=(1000, 3000),
        elevation_min=900,
        elevation_max=3500,
        height_diff_up=(200, None),
        route_length=(None, 10000),
        orientations=["W", "S"],
        route_types=["rock_climbing"],
        global_rating=("AD", "D+"),
        rock_free_rating=("6a", "6c+"),
        rock_required_rating=("5c", None),
        mtb_length_asphalt=(0, 5),
        rock_types=["limestone"],
        extras={"prom": 300},
    )
    q = p.to_query_params()
    assert q["q"] == "alps"
    assert q["lang"] == "fr"
    assert q["bbox"] == "0,1,2,3"
    assert q["fields"] == "a,b"
    assert q["orderby"] == "elevation_max"
    assert q["order"] == "desc"
    assert q["limit"] == 50 and q["offset"] == 10
    assert q["act"] == "rock_climbing,mountain_climbing"
    assert q["w"] == "123,456" and q["u"] == "789"
    assert q["ele"] == "1000,3000"
    assert q["rmina"] == 900 and q["rmaxa"] == 3500
    assert q["hdif"] == "200,"
    assert q["rlen"] == ",10000"
    assert q["fac"] == "W,S"
    assert q["rtyp"] == "rock_climbing"
    assert q["grat"] == "AD,D+"
    assert q["frat"] == "6a,6c+"
    assert q["rrat"] == "5c,"
    assert q["mbroad"] == "0,5"
    assert q["rock"] == "limestone"
    assert q["prom"] == 300


def test_waypoint_params_to_query():
    p = WaypointSearchParams(
        wtyp=["paragliding_takeoff", "summit"],
        act="mountain_climbing",
        elevation=("1000", "2000"),
        prominence=(300, None),
        height_min=(None, 50),
        routes_quantity=(10, 100),
        rock_types=["limestone", "granite"],
        orientations=["N"],
        best_periods=["spring", "autumn"],
        lift_access=True,
        access_time=("30min", "1h"),
        climbing_rating_max=("6a", "7a"),
        paragliding_rating=("2", "4"),
        weather_station_types=["rain"],
        public_transportation_types=["bus"],
        public_transportation_rating="great",
        snow_clearance_rating="excellent",
        product_types=["guidebook"],
    )
    q = p.to_query_params()
    assert q["wtyp"] == "paragliding_takeoff,summit"
    assert q["act"] == "mountain_climbing"
    assert q["walt"] == "1000,2000"
    assert q["prom"] == "300,"
    assert q["tminh"] == ",50"
    assert q["rqua"] == "10,100"
    assert q["wrock"] == "limestone,granite"
    assert q["wfac"] == "N"
    assert q["period"] == "spring,autumn"
    assert q["plift"] == "true"
    assert q["tappt"] == "30min,1h"
    assert q["tmaxr"] == "6a,7a"
    assert q["pgrat"] == "2,4"
    assert q["whtyp"] == "rain"
    assert q["tpty"] == "bus"
    assert q["tp"] == "great"
    assert q["psnow"] == "excellent"
    assert q["ftyp"] == "guidebook"
