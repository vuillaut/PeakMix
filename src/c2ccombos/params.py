from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Tuple, Union

Number = Union[int, float]


def _join_list(v: Union[str, Iterable[Any], None]) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return ",".join([str(s) for s in v])


def _bbox_to_param(bbox: Optional[Tuple[float, float, float, float]]) -> Optional[str]:
    if not bbox:
        return None
    return f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"


def _format_range(value: Union[str, Tuple[Optional[Number], Optional[Number]], None]) -> Optional[str]:
    """Format a range value accepted by the C2C API as "min,max".

    - Accepts a string already formatted, returns as-is.
    - Accepts a tuple (min, max); allows None for open bounds.
    - Returns None if value is None.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    lo, hi = value
    lo_s = "" if lo is None else str(lo)
    hi_s = "" if hi is None else str(hi)
    return f"{lo_s},{hi_s}"


@dataclass
class BaseSearchParams:
    q: Optional[str] = None
    lang: Optional[str] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    fields: Optional[Iterable[str]] = None
    orderby: Optional[str] = None
    order: Optional[str] = None  # asc|desc
    limit: Optional[int] = None
    offset: Optional[int] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> "BaseSearchParams":
        self.extras[key] = value
        return self

    def to_query_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if self.q is not None:
            params["q"] = self.q
        if self.lang is not None:
            params["lang"] = self.lang
        if self.bbox is not None:
            params["bbox"] = _bbox_to_param(self.bbox)
        if self.fields is not None:
            params["fields"] = _join_list(self.fields)
        if self.orderby is not None:
            params["orderby"] = self.orderby
        if self.order is not None:
            params["order"] = self.order
        if self.limit is not None:
            params["limit"] = int(self.limit)
        if self.offset is not None:
            params["offset"] = int(self.offset)
        # Merge extras last (let callers override)
        for k, v in self.extras.items():
            if v is not None:
                if isinstance(v, (list, tuple)):
                    params[k] = _join_list(v)  # join list of strings
                else:
                    params[k] = v
        return params


@dataclass
class RouteSearchParams(BaseSearchParams):
    # Common filters
    act: Optional[Union[str, Iterable[str]]] = None  # activities -> act

    # IDs
    waypoints: Optional[Union[str, Iterable[Union[str, int]]]] = None  # associated waypoint ids -> w
    users: Optional[Union[str, Iterable[Union[str, int]]]] = None  # associated user ids -> u

    # Elevation & lengths
    elevation: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # combined -> ele
    elevation_min: Optional[int] = None  # -> rmina
    elevation_max: Optional[int] = None  # -> rmaxa
    height_diff_up: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> hdif
    height_diff_down: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> ddif
    route_length: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> rlen
    difficulties_height: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> ralt
    height_diff_access: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> rappr
    height_diff_difficulties: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> dhei

    # Enums / arrays
    route_types: Optional[Union[str, Iterable[str]]] = None  # -> rtyp
    orientations: Optional[Union[str, Iterable[str]]] = None  # -> fac
    durations: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> time (enum range)
    glacier_gear: Optional[str] = None  # -> glac
    configuration: Optional[Union[str, Iterable[str]]] = None  # -> conf

    # Ratings (enum ranges)
    ski_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> trat
    ski_exposition: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> sexpo
    labande_ski_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> srat
    labande_global_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> lrat
    global_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> grat
    engagement_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> erat
    risk_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> orrat
    equipment_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> prat
    ice_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> irat
    mixed_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> mrat
    exposition_rock_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> rexpo
    rock_free_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> frat
    rock_required_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> rrat
    aid_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> arat
    via_ferrata_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> krat
    hiking_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> hrat
    hiking_mtb_exposition: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> hexpo
    snowshoe_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> wrat
    mtb_up_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> mbur
    mtb_down_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> mbdr

    # MTB numeric fields
    mtb_length_asphalt: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> mbroad
    mtb_length_trail: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> mbtrack
    mtb_height_diff_portages: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> mbpush

    # Rock / styles
    rock_types: Optional[Union[str, Iterable[str]]] = None  # -> rock
    climbing_outdoor_type: Optional[Union[str, Iterable[str]]] = None  # -> crtyp
    slackline_type: Optional[str] = None  # -> sltyp

    def to_query_params(self) -> Dict[str, Any]:
        params = super().to_query_params()
        # Basic
        if self.act is not None:
            params["act"] = _join_list(self.act if not isinstance(self.act, str) else self.act)

        # IDs
        if self.waypoints is not None:
            params["w"] = _join_list(self.waypoints if not isinstance(self.waypoints, str) else self.waypoints)
        if self.users is not None:
            params["u"] = _join_list(self.users if not isinstance(self.users, str) else self.users)

        # Elevations / lengths
        ele = _format_range(self.elevation)
        if ele is not None:
            params["ele"] = ele
        if self.elevation_min is not None:
            params["rmina"] = int(self.elevation_min)
        if self.elevation_max is not None:
            params["rmaxa"] = int(self.elevation_max)
        if (v := _format_range(self.height_diff_up)) is not None:
            params["hdif"] = v
        if (v := _format_range(self.height_diff_down)) is not None:
            params["ddif"] = v
        if (v := _format_range(self.route_length)) is not None:
            params["rlen"] = v
        if (v := _format_range(self.difficulties_height)) is not None:
            params["ralt"] = v
        if (v := _format_range(self.height_diff_access)) is not None:
            params["rappr"] = v
        if (v := _format_range(self.height_diff_difficulties)) is not None:
            params["dhei"] = v

        # Enums / arrays
        if self.route_types is not None:
            params["rtyp"] = _join_list(self.route_types if not isinstance(self.route_types, str) else self.route_types)
        if self.orientations is not None:
            params["fac"] = _join_list(self.orientations if not isinstance(self.orientations, str) else self.orientations)
        if (v := _format_range(self.durations)) is not None:
            params["time"] = v
        if self.glacier_gear is not None:
            params["glac"] = self.glacier_gear
        if self.configuration is not None:
            params["conf"] = _join_list(self.configuration if not isinstance(self.configuration, str) else self.configuration)

        # Ratings (enum ranges)
        for attr, key in [
            ("ski_rating", "trat"),
            ("ski_exposition", "sexpo"),
            ("labande_ski_rating", "srat"),
            ("labande_global_rating", "lrat"),
            ("global_rating", "grat"),
            ("engagement_rating", "erat"),
            ("risk_rating", "orrat"),
            ("equipment_rating", "prat"),
            ("ice_rating", "irat"),
            ("mixed_rating", "mrat"),
            ("exposition_rock_rating", "rexpo"),
            ("rock_free_rating", "frat"),
            ("rock_required_rating", "rrat"),
            ("aid_rating", "arat"),
            ("via_ferrata_rating", "krat"),
            ("hiking_rating", "hrat"),
            ("hiking_mtb_exposition", "hexpo"),
            ("snowshoe_rating", "wrat"),
            ("mtb_up_rating", "mbur"),
            ("mtb_down_rating", "mbdr"),
        ]:
            v = getattr(self, attr)
            if (rng := _format_range(v)) is not None:
                params[key] = rng

        # MTB numeric fields
        if (v := _format_range(self.mtb_length_asphalt)) is not None:
            params["mbroad"] = v
        if (v := _format_range(self.mtb_length_trail)) is not None:
            params["mbtrack"] = v
        if (v := _format_range(self.mtb_height_diff_portages)) is not None:
            params["mbpush"] = v

        # Rock / styles
        if self.rock_types is not None:
            params["rock"] = _join_list(self.rock_types if not isinstance(self.rock_types, str) else self.rock_types)
        if self.climbing_outdoor_type is not None:
            params["crtyp"] = _join_list(self.climbing_outdoor_type if not isinstance(self.climbing_outdoor_type, str) else self.climbing_outdoor_type)
        if self.slackline_type is not None:
            params["sltyp"] = self.slackline_type
        return params


@dataclass
class WaypointSearchParams(BaseSearchParams):
    # Common
    act: Optional[Union[str, Iterable[str]]] = None  # activities -> act
    wtyp: Optional[Union[str, Iterable[str]]] = None  # waypoint types -> wtyp

    # Numeric ranges
    elevation: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> walt
    prominence: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> prom
    height_min: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> tminh
    height_max: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> tmaxh
    height_median: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> tmedh
    routes_quantity: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> rqua
    length: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> len
    capacity: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> hucap
    capacity_staffed: Optional[Union[str, Tuple[Optional[Number], Optional[Number]]]] = None  # -> hscap

    # Enums / arrays
    rock_types: Optional[Union[str, Iterable[str]]] = None  # -> wrock
    orientations: Optional[Union[str, Iterable[str]]] = None  # -> wfac
    best_periods: Optional[Union[str, Iterable[str]]] = None  # -> period
    lift_access: Optional[Union[bool, str]] = None  # -> plift
    custodianship: Optional[str] = None  # -> hsta
    climbing_styles: Optional[Union[str, Iterable[str]]] = None  # -> tcsty
    access_time: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> tappt (enum range)
    climbing_rating_max: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> tmaxr
    climbing_rating_min: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> tminr
    climbing_rating_median: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> tmedr
    children_proof: Optional[str] = None  # -> chil
    rain_proof: Optional[str] = None  # -> rain
    climbing_outdoor_types: Optional[Union[str, Iterable[str]]] = None  # -> ctout
    climbing_indoor_types: Optional[Union[str, Iterable[str]]] = None  # -> ctin
    paragliding_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> pgrat
    exposition_rating: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> pglexp
    weather_station_types: Optional[Union[str, Iterable[str]]] = None  # -> whtyp
    equipment_ratings: Optional[Union[str, Tuple[Optional[str], Optional[str]]]] = None  # -> anchq
    public_transportation_types: Optional[Union[str, Iterable[str]]] = None  # -> tpty
    public_transportation_rating: Optional[str] = None  # -> tp
    snow_clearance_rating: Optional[str] = None  # -> psnow
    product_types: Optional[Union[str, Iterable[str]]] = None  # -> ftyp

    def to_query_params(self) -> Dict[str, Any]:
        params = super().to_query_params()
        if self.act is not None:
            params["act"] = _join_list(self.act if not isinstance(self.act, str) else self.act)
        if self.wtyp is not None:
            params["wtyp"] = _join_list(self.wtyp if not isinstance(self.wtyp, str) else self.wtyp)
        # Numeric ranges
        for attr, key in [
            ("elevation", "walt"),
            ("prominence", "prom"),
            ("height_min", "tminh"),
            ("height_max", "tmaxh"),
            ("height_median", "tmedh"),
            ("routes_quantity", "rqua"),
            ("length", "len"),
            ("capacity", "hucap"),
            ("capacity_staffed", "hscap"),
        ]:
            v = getattr(self, attr)
            if (rng := _format_range(v)) is not None:
                params[key] = rng

        # Enums / arrays
        if self.rock_types is not None:
            params["wrock"] = _join_list(self.rock_types if not isinstance(self.rock_types, str) else self.rock_types)
        if self.orientations is not None:
            params["wfac"] = _join_list(self.orientations if not isinstance(self.orientations, str) else self.orientations)
        if self.best_periods is not None:
            params["period"] = _join_list(self.best_periods if not isinstance(self.best_periods, str) else self.best_periods)
        if self.lift_access is not None:
            params["plift"] = str(self.lift_access).lower() if isinstance(self.lift_access, bool) else self.lift_access
        if self.custodianship is not None:
            params["hsta"] = self.custodianship
        if self.climbing_styles is not None:
            params["tcsty"] = _join_list(self.climbing_styles if not isinstance(self.climbing_styles, str) else self.climbing_styles)
        for attr, key in [
            ("access_time", "tappt"),
            ("climbing_rating_max", "tmaxr"),
            ("climbing_rating_min", "tminr"),
            ("climbing_rating_median", "tmedr"),
            ("paragliding_rating", "pgrat"),
            ("exposition_rating", "pglexp"),
            ("equipment_ratings", "anchq"),
        ]:
            v = getattr(self, attr)
            if (rng := _format_range(v)) is not None:
                params[key] = rng
        if self.climbing_outdoor_types is not None:
            params["ctout"] = _join_list(self.climbing_outdoor_types if not isinstance(self.climbing_outdoor_types, str) else self.climbing_outdoor_types)
        if self.climbing_indoor_types is not None:
            params["ctin"] = _join_list(self.climbing_indoor_types if not isinstance(self.climbing_indoor_types, str) else self.climbing_indoor_types)
        if self.weather_station_types is not None:
            params["whtyp"] = _join_list(self.weather_station_types if not isinstance(self.weather_station_types, str) else self.weather_station_types)
        if self.public_transportation_types is not None:
            params["tpty"] = _join_list(self.public_transportation_types if not isinstance(self.public_transportation_types, str) else self.public_transportation_types)
        if self.public_transportation_rating is not None:
            params["tp"] = self.public_transportation_rating
        if self.snow_clearance_rating is not None:
            params["psnow"] = self.snow_clearance_rating
        if self.product_types is not None:
            params["ftyp"] = _join_list(self.product_types if not isinstance(self.product_types, str) else self.product_types)
        return params
