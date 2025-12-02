# server/utils/ml.py

import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

DB_PATH = "db/analytics.sqlite"

def predictive_correction():
    """
    Prédit les corrections GPS à partir de l'historique.
    Retourne une liste de dict avec lat/lon prédit.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT latitude, longitude, corrected_lat, corrected_lon FROM gps_history")
    rows = c.fetchall()
    conn.close()

    if len(rows) < 5:
        return []

    # Préparer les données pour la régression
    X = np.array([[lat, lon] for lat, lon, _, _ in rows])
    y_lat = np.array([corr_lat for _, _, corr_lat, _ in rows])
    y_lon = np.array([corr_lon for _, _, _, corr_lon in rows])

    # Modèles pour latitude et longitude
    model_lat = LinearRegression().fit(X, y_lat)
    model_lon = LinearRegression().fit(X, y_lon)

    # Prédiction pour tous les points actuels
    predictions = []
    for lat, lon, _, _ in rows:
        pred_lat = model_lat.predict([[lat, lon]])[0]
        pred_lon = model_lon.predict([[lat, lon]])[0]
        predictions.append({"pred_lat": pred_lat, "pred_lon": pred_lon})

    return predictions
