from __future__ import annotations

from typing import Mapping, Optional


def doc_entity(doc: Mapping) -> Optional[str]:
    """Infer C2C entity path (routes, waypoints, etc.) from a document.

    Prefers `type` short code if present, else uses simple heuristics.
    """
    t = doc.get("type")
    if isinstance(t, str):
        mapping = {
            "r": "routes",
            "w": "waypoints",
            "o": "outings",
            "a": "areas",
            "i": "images",
            "b": "books",
            "c": "articles",
            "x": "xreports",
            "u": "users",
        }
        return mapping.get(t)

    # Heuristics
    if "waypoint_type" in doc:
        return "waypoints"
    if "activities" in doc:
        return "routes"
    return None


def doc_id(doc: Mapping) -> Optional[int]:
    return doc.get("document_id") or doc.get("id")


def doc_url(doc: Mapping, base: str = "https://www.camptocamp.org") -> Optional[str]:
    entity = doc_entity(doc)
    did = doc_id(doc)
    if not entity or not did:
        return None
    return f"{base.rstrip('/')}/{entity}/{did}"
