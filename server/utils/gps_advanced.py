# server/utils/gps_advanced.py
import time
from server.db import get_conn
from server.utils.gps import haversine_distance
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

MODEL_FILE = Path(__file__).parent.parent / "ml_model.pkl"
SCALER_FILE = Path(__file__).parent.parent / "ml_scaler.pkl"

def store_point(point):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO gps_points(device_id, lat, lon, accuracy, source, timestamp, corrected_lat, corrected_lon, correction_reason)
    VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        point.get("device_id"),
        point.get("lat"),
        point.get("lon"),
        point.get("accuracy"),
        point.get("source", "device"),
        point.get("timestamp"),
        point.get("corrected_lat"),
        point.get("corrected_lon"),
        point.get("correction_reason")
    ))
    conn.commit()

def fetch_recent(device_id, limit=50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gps_points WHERE device_id=? ORDER BY timestamp DESC LIMIT ?", (device_id, limit))
    rows = cur.fetchall()
    return [dict(r) for r in rows]

def compute_fusion(device, geocode, device_accuracy=None):
    """
    device: dict with lat, lon, accuracy (m)
    geocode: dict with lat, lon (from address)
    Returns weighted fusion: higher weight to device when accuracy low (<10m)
    Uses dynamic weighting and history.
    """
    # baseline weights
    if device_accuracy is None:
        device_accuracy = device.get("accuracy", 50.0)
    # convert accuracy to weight: lower accuracy => lower weight
    # weight_device = 1 / (1 + accuracy/10)  -> tuned
    weight_device = 1.0 / (1.0 + device_accuracy / 20.0)
    weight_geocode = 1.0 - weight_device
    # clamp
    weight_device = max(0.05, min(0.95, weight_device))
    weight_geocode = 1.0 - weight_device

    fused_lat = device["lat"] * weight_device + geocode["lat"] * weight_geocode
    fused_lon = device["lon"] * weight_device + geocode["lon"] * weight_geocode

    # compute distance between device and geocode
    dist = haversine_distance(device["lat"], device["lon"], geocode["lat"], geocode["lon"])
    reason = f"fusion device/geocode dist={int(dist)}m acc={device_accuracy}m"

    return {
        "corrected_lat": fused_lat,
        "corrected_lon": fused_lon,
        "used_weight_device": weight_device,
        "used_weight_geocode": weight_geocode,
        "reason": reason,
        "distance_device_geocode": dist
    }

# Light-weight online learning placeholder: keeps running mean of offsets per geohash (coarse)
import math, hashlib

def geohash_key(lat, lon, precision=2):
    # coarse grid key (not true geohash) e.g. 2 decimal degrees
    key = f"{round(lat, precision)}:{round(lon, precision)}"
    return key

def update_historical_offsets(lat, lon, corrected_lat, corrected_lon):
    conn = get_conn()
    cur = conn.cursor()
    # store in gps_points already; but here we could build aggregated offsets in analytics_cache
    offset_lat = corrected_lat - lat
    offset_lon = corrected_lon - lon
    key = geohash_key(lat, lon, precision=2)
    cur.execute("INSERT INTO analytics_cache(key, value, timestamp) VALUES(?,?,?)",
                (f"offset:{key}", f"{offset_lat},{offset_lon}", int(time.time())))
    conn.commit()

def compute_historical_bias(lat, lon):
    conn = get_conn()
    cur = conn.cursor()
    key = geohash_key(lat, lon, precision=2)
    cur.execute("SELECT value FROM analytics_cache WHERE key LIKE ?", (f"offset:{key}%",))
    rows = cur.fetchall()
    if not rows:
        return None
    vals = [tuple(map(float, r["value"].split(","))) for r in rows]
    mean_lat = sum(v[0] for v in vals)/len(vals)
    mean_lon = sum(v[1] for v in vals)/len(vals)
    return {"bias_lat": mean_lat, "bias_lon": mean_lon}
