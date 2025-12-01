# server/utils/analytics.py
from server.db import get_conn
from server.utils.gps import haversine_distance
import time
import json

def stats_overall(since_ts=0):
    conn = get_conn()
    cur = conn.cursor()
    q = "SELECT COUNT(*) as cnt, AVG(accuracy) as avg_acc FROM gps_points WHERE timestamp>=?"
    cur.execute(q, (since_ts,))
    row = cur.fetchone()
    return {"count": row["cnt"], "avg_accuracy": row["avg_acc"]}

def heatmap_points(limit=10000):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon FROM gps_points ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    points = [{"lat": r["lat"], "lon": r["lon"]} for r in rows]
    return points

def distance_by_device(device_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gps_points WHERE device_id=? ORDER BY timestamp ASC", (device_id,))
    rows = cur.fetchall()
    total = 0.0
    prev = None
    for r in rows:
        if prev:
            total += haversine_distance(prev["lat"], prev["lon"], r["lat"], r["lon"])
        prev = r
    return {"device_id": device_id, "distance_m": total}

def problematic_zones(threshold=500):
    """
    simple heuristic: find clusters of points where accuracy worse than threshold
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon, accuracy FROM gps_points WHERE accuracy>? ORDER BY timestamp DESC LIMIT 5000", (threshold,))
    rows = cur.fetchall()
    zones = [{"lat": r["lat"], "lon": r["lon"], "accuracy": r["accuracy"]} for r in rows]
    return zones
