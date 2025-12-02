from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import requests
import datetime
import os
import time
import math
import jwt
import numpy as np
from sklearn.linear_model import LinearRegression
import uvicorn
from collections import defaultdict

# ======== CONFIG ========
DB_PATH = os.path.join("db", "analytics.sqlite")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"

JWT_SECRET = "TonSecretSuperFort"
JWT_ALGORITHM = "HS256"
RATE_LIMIT = 10
TIME_WINDOW = 60  # secondes
requests_history = defaultdict(list)

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
    os.makedirs("db", exist_ok=True)
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
    c.execute(
        "INSERT INTO gps_history (latitude, longitude, corrected_lat, corrected_lon, address, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (lat, lon, corr_lat, corr_lon, address, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

# ======== RATE LIMITING ========
def check_rate_limit(ip: str):
    now = time.time()
    requests_history[ip] = [t for t in requests_history[ip] if now - t < TIME_WINDOW]
    if len(requests_history[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Trop de requêtes")
    requests_history[ip].append(now)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    check_rate_limit(ip)
    response = await call_next(request)
    return response

# ======== JWT UTIL ========
def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")

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

# ======== MACHINE LEARNING ========
def predictive_correction():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT latitude, longitude, corrected_lat, corrected_lon FROM gps_history")
    rows = c.fetchall()
    conn.close()

    if len(rows) < 5:
        return []

    X = np.array([[lat, lon] for lat, lon, _, _ in rows])
    y_lat = np.array([corr_lat for _, _, corr_lat, _ in rows])
    y_lon = np.array([corr_lon for _, _, _, corr_lon in rows])

    model_lat = LinearRegression().fit(X, y_lat)
    model_lon = LinearRegression().fit(X, y_lon)

    predictions = []
    for lat, lon, _, _ in rows:
        pred_lat = model_lat.predict([[lat, lon]])[0]
        pred_lon = model_lon.predict([[lat, lon]])[0]
        predictions.append({"pred_lat": pred_lat, "pred_lon": pred_lon})

    return predictions

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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), MAX(timestamp) FROM gps_history")
    count, last_ts = c.fetchone()
    c.execute("SELECT corrected_lat, corrected_lon FROM gps_history")
    points = [{"lat": lat, "lon": lon} for lat, lon in c.fetchall()]
    conn.close()
    return {"total_points": count, "last_correction": last_ts, "points": points}

@app.get("/predictive")
def predictive():
    return predictive_correction()

@app.get("/secure-analytics")
def secure_analytics(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    verify_token(token)
    return analytics()

# ======== INIT DB ========
init_db()

# ======== RUN ========
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
