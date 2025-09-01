from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Axis-aligned bounding box in EPSG:3857 (C2C web mercator meters).

    Order: minx, miny, maxx, maxy (consistent with API bbox param)
    """

    minx: float
    miny: float
    maxx: float
    maxy: float

    def to_query(self) -> str:
        return f"{self.minx:.0f},{self.miny:.0f},{self.maxx:.0f},{self.maxy:.0f}"


class Geometry(BaseModel):
    type: str
    coordinates: list


class Waypoint(BaseModel):
    id: int
    type: str = Field(alias="type")
    elevation: Optional[float] = None
    name: Optional[str] = None
    main_waypoint_type: Optional[str] = None
    geometry: Optional[Geometry] = None


class Route(BaseModel):
    id: int
    activities: List[str] = Field(default_factory=list)
    elevation_min: Optional[float] = None
    elevation_max: Optional[float] = None
    name: Optional[str] = None
    geometry: Optional[Geometry] = None


class PaginatedResponse(BaseModel):
    total: int
    documents: list

    @property
    def items(self) -> list:
        return self.documents
