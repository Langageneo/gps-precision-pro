import sqlite3
from datetime import datetime
DB_PATH = 'db/analytics.sqlite'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def compute_driver_scores(limit=1000):
    """
    Calcule le score des livreurs sur la base d'historique :
    - plus de livraisons positives augmente le score
    - pénalités pour lenteur / erreurs GPS répétées
    """
    conn = get_db()
    cur = conn.cursor()
    # Exemple simple : score = deliveries_normalized * 0.7 + reliability * 0.3
    cur.execute("""
        SELECT livreur_id,
               COUNT(*) AS deliveries,
               AVG(COALESCE(score, 1.0)) AS avg_score
        FROM analytics
        GROUP BY livreur_id
        ORDER BY deliveries DESC
        LIMIT ?
    """, (limit,))
    rows = []
    for r in cur.fetchall():
        deliveries = r["deliveries"]
        avg = r["avg_score"] or 1.0
        score = (deliveries / (deliveries + 10)) * 0.7 + (avg / 5.0) * 0.3
        rows.append({
            "livreur_id": r["livreur_id"],
            "deliveries": deliveries,
            "avg_score": avg,
            "score": round(score, 4)
        })
    conn.close()
    return rows

def get_best_driver():
    scores = compute_driver_scores()
    if not scores:
        return {}
    best = max(scores, key=lambda x: x["score"])
    return best
