import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'db/analytics.sqlite'

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def zones_with_high_volume(window_minutes=60, threshold=50):
    conn = _get_conn()
    cur = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(minutes=window_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        SELECT zone, COUNT(*) AS nb
        FROM analytics
        WHERE timestamp >= ?
        GROUP BY zone
        HAVING nb > ?
    """, (cutoff, threshold))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def generate_alerts():
    # Retourne alertes prêtes à consommer par API
    hot_zones = zones_with_high_volume()
    alerts = []
    for z in hot_zones:
        alerts.append({
            "zone": z["zone"],
            "type": "high_volume",
            "severity": "high",
            "count": z["nb"],
            "created_at": datetime.utcnow().isoformat() + "Z"
        })
    return alerts
