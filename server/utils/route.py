# server/utils/route.py
import httpx
from server.config import OSRM_URL

def get_route(points, profile="driving"):
    """
    points: list of [lon, lat] pairs
    returns distance (m), duration (s), geometry (polyline)
    Uses OSRM route service.
    """
    coords = ";".join([f"{p[0]},{p[1]}" for p in points])
    url = f"{OSRM_URL}/route/v1/{profile}/{coords}"
    params = {"overview": "full", "geometries": "polyline", "steps": "false"}
    r = httpx.get(url, params=params, timeout=10.0)
    r.raise_for_status()
    d = r.json()
    if "routes" not in d or not d["routes"]:
        raise RuntimeError("No route")
    route = d["routes"][0]
    return {"distance": route["distance"], "duration": route["duration"], "geometry": route["geometry"]}
