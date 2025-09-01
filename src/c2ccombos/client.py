from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

import requests

log = logging.getLogger(__name__)


class C2CClient:
    """Lightweight client for the CampToCamp API.

    - Handles base URL, timeouts, and common params.
    - Exposes a single request method and convenience wrappers.
    - Does not model every endpoint; keep generic and composable.
    """

    def __init__(
        self,
        base_url: str = "https://api.camptocamp.org",
        timeout: float = 15.0,
        default_params: Optional[Mapping[str, Any]] = None,
        session: Optional[requests.Session] = None,
        user_agent: str = "c2ccombos/0.1 (+https://github.com/vuillaut/c2ccombos)",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_params = dict(default_params or {})
        self.session = session or requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": user_agent,
        })

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform an HTTP request and return JSON.

        Raises requests.HTTPError on non-2xx responses.
        """
        url = self._build_url(path)
        merged = dict(self.default_params)
        if params:
            # Keep falsy but not None (e.g., 0) and drop None values
            merged.update({k: v for k, v in params.items() if v is not None})

        log.debug("C2C %s %s params=%s", method, url, merged)
        resp = self.session.request(method.upper(), url, params=merged, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # Convenience wrappers
    def get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return self.request("GET", path, params=params)

    # Endpoint helpers kept generic to encourage reuse
    def list_routes(self, **params: Any) -> Dict[str, Any]:
        return self.get("routes", params=params)

    def list_waypoints(self, **params: Any) -> Dict[str, Any]:
        return self.get("waypoints", params=params)
