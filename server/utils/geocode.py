# server/utils/geocode.py
import httpx
import time
from server.config import NOMINATIM_URL, NOMINATIM_REVERSE
from server.db import get_conn

HEADERS = {"User-Agent": "gps-precision-analytics/1.0 (+https://example.com)"}

def geocode(address, limit=1):
    """
    Use Nominatim search to geocode an address string.
    Caches results in SQLite to avoid throttling.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon, display_name FROM address_cache WHERE query=?", (address,))
    row = cur.fetchone()
    if row:
        return {"lat": row["lat"], "lon": row["lon"], "display_name": row["display_name"], "cached": True}
    params = {"q": address, "format": "jsonv2", "limit": limit}
    try:
        r = httpx.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        d = data[0]
        lat = float(d["lat"])
        lon = float(d["lon"])
        display = d.get("display_name", "")
        cur.execute("INSERT OR REPLACE INTO address_cache(query, lat, lon, display_name, timestamp) VALUES(?,?,?,?,?)",
                    (address, lat, lon, display, int(time.time())))
        conn.commit()
        return {"lat": lat, "lon": lon, "display_name": display, "cached": False}
    except Exception as e:
        return None

def reverse_geocode(lat, lon):
    params = {"lat": lat, "lon": lon, "format": "jsonv2"}
    r = httpx.get(NOMINATIM_REVERSE, params=params, headers=HEADERS, timeout=10.0)
    r.raise_for_status()
    return r.json()
