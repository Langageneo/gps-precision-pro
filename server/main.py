from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import requests
import datetime
import math
import uvicorn
import os

# ======== CONFIG ========
DB_PATH = os.path.join("db", "analytics.sqlite")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"

# ======== APP ========
app = FastAPI(title="GPS Dashboard API")

# ======== CORS ========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # changer en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== MODELS ========
class AddressRequest(BaseModel):
    address: str

class GPSRequest(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class RouteRequest(BaseModel):
    waypoints: List[List[float]]  # [[lat, lon], ...]

# ======== DATABASE UTILS ========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS gps_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitude REAL,
        longitude REAL,
        corrected_lat REAL,
        corrected_lon REAL,
        address TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_gps(lat, lon, corr_lat, corr_lon, address):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO gps_history (latitude, longitude, corrected_lat, corrected_lon, address, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (lat, lon, corr_lat, corr_lon, address, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

# ======== UTILITIES ========
def geocode_address(address):
    params = {"q": address, "format": "json"}
    try:
        r = requests.get(NOMINATIM_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            raise ValueError("Address not found")
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def correct_gps(lat, lon, address=None):
    """Combine device GPS + geocoding to correct position"""
    if address:
        try:
            geo_lat, geo_lon = geocode_address(address)
            # pondération simple : device 70%, geocode 30%
            corr_lat = 0.7 * lat + 0.3 * geo_lat
            corr_lon = 0.7 * lon + 0.3 * geo_lon
        except:
            corr_lat, corr_lon = lat, lon
    else:
        corr_lat, corr_lon = lat, lon
    return corr_lat, corr_lon

def calculate_route(waypoints):
    coords = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
    url = f"{OSRM_URL}/{coords}?overview=full&geometries=geojson"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching route")
    data = r.json()
    return data.get("routes", [])

# ======== ROUTES ========
@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/validate-address")
def validate_address(req: AddressRequest):
    lat, lon = geocode_address(req.address)
    return {"latitude": lat, "longitude": lon}

@app.post("/gps-correct")
def gps_correct(req: GPSRequest):
    corr_lat, corr_lon = correct_gps(req.latitude, req.longitude, req.address)
    save_gps(req.latitude, req.longitude, corr_lat, corr_lon, req.address)
    return {"corrected_latitude": corr_lat, "corrected_longitude": corr_lon}

@app.post("/get-optimized-route")
def get_optimized_route(req: RouteRequest):
    routes = calculate_route(req.waypoints)
    return {"routes": routes}

@app.get("/analytics")
def analytics():
    """Return simple analytics: total points, heatmap points, last corrections"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), MAX(timestamp) FROM gps_history")
    count, last_ts = c.fetchone()
    c.execute("SELECT corrected_lat, corrected_lon FROM gps_history")
    points = [{"lat": lat, "lon": lon} for lat, lon in c.fetchall()]
    conn.close()
    return {"total_points": count, "last_correction": last_ts, "points": points}

# ======== INIT DB ========
init_db()

# ======== RUN ========
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
