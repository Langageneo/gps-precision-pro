import sqlite3
from datetime import datetime
from collections import Counter

DB_PATH = 'db/analytics.sqlite'

# Connexion SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 1️⃣ Tous les analytics globaux
def get_all_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analytics")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

# 2️⃣ Analytics détaillés pour chaque livreur
def get_livreurs_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT livreur_id, COUNT(*) AS livraisons, 
               SUM(distance) AS distance_totale, 
               AVG(score) AS score_moyen
        FROM analytics
        GROUP BY livreur_id
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

# 3️⃣ Meilleur livreur
def get_best_livreur():
    livreurs = get_livreurs_stats()
    if not livreurs:
        return {}
    # Score pondéré : 50% distance, 50% score_moyen
    for l in livreurs:
        l['score_pondere'] = l['distance_totale']*0.5 + l['score_moyen']*0.5
    best = max(livreurs, key=lambda x: x['score_pondere'])
    return best

# 4️⃣ Produits les plus populaires
def get_popular_products(top_n=10):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_name FROM analytics")
    products = [row['product_name'] for row in cur.fetchall()]
    conn.close()
    counter = Counter(products)
    return counter.most_common(top_n)

# 5️⃣ Heatmap zones
def get_heatmap_zones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude FROM analytics")
    points = [dict(row) for row in cur.fetchall()]
    conn.close()
    return points

# 6️⃣ Alertes dynamiques (zones congestion, pics)
def get_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    # Exemple simple : zones avec >50 livraisons en 1h
    cur.execute("""
        SELECT zone, COUNT(*) AS nb_livraisons
        FROM analytics
        WHERE timestamp >= datetime('now','-1 hour')
        GROUP BY zone
        HAVING nb_livraisons > 50
    """)
    alerts = [dict(row) for row in cur.fetchall()]
    conn.close()
    return alerts

# 7️⃣ Prédictions simples
def predictive_suggestions():
    # Basé sur historique : zones avec + de livraisons récurrentes
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT zone FROM analytics")
    zones = [row['zone'] for row in cur.fetchall()]
    conn.close()
    counter = Counter(zones)
    top_zones = counter.most_common(5)
    return {"zones_a_surveiller": top_zones}
