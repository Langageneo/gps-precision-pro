# server/main.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3
import time
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
import jwt

# ======================
# CONFIGURATION
# ======================
DB_PATH = "db/analytics.sqlite"
JWT_SECRET = "ton_secret_ici"
RATE_LIMIT = 10
TIME_WINDOW = 60

# ======================
# INITIALISATION APP
# ======================
app = FastAPI(title="GPS Dashboard API")

# ======================
# RATE LIMITING
# ======================
requests_history = defaultdict(list)

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

# ======================
# JWT AUTH
# ======================
security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

# ======================
# UTILITAIRES
# ======================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ======================
# MACHINE LEARNING LEGER
# ======================
def predictive_correction():
    conn = get_db_connection()
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

@app.get("/predictive", dependencies=[Depends(verify_jwt)])
def predictive():
    return predictive_correction()

# ======================
# ROUTES GPS & ANALYTICS
# ======================
@app.get("/validate-address", dependencies=[Depends(verify_jwt)])
def validate_address(address: str):
    # à compléter avec Nominatim
    return {"address": address, "lat": 0.0, "lon": 0.0}

@app.post("/gps-correct", dependencies=[Depends(verify_jwt)])
def gps_correct(lat: float, lon: float):
    # Correction GPS pondérée device + historique
    corrected_lat = lat + 0.0001
    corrected_lon = lon + 0.0001

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO gps_history (latitude, longitude, corrected_lat, corrected_lon) VALUES (?, ?, ?, ?)",
        (lat, lon, corrected_lat, corrected_lon)
    )
    conn.commit()
    conn.close()

    return {"corrected_lat": corrected_lat, "corrected_lon": corrected_lon}

@app.get("/get-optimized-route", dependencies=[Depends(verify_jwt)])
def get_optimized_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    # Appel OSRM ou calcul simple
    route = [{"lat": start_lat, "lon": start_lon}, {"lat": end_lat, "lon": end_lon}]
    return {"route": route}

@app.get("/analytics", dependencies=[Depends(verify_jwt)])
def analytics():
    # Exemple simple analytics
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total_points FROM gps_history")
    total_points = c.fetchone()["total_points"]
    conn.close()
    return {"total_points": total_points}

# ======================
# ROUTE TEST TOKEN
# ======================
@app.get("/token")
def get_token():
    payload = {"user": "admin"}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"token": token}

# ======================
# RUN SERVER
# ======================
# uvicorn main:app --reload
