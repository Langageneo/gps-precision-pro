"""
Simple script d'entraînement ML pour GPS bias.
Utilise l'historique corrections_history pour assembler X,y.
Exécution : python server/ai/train.py
"""
import sqlite3
import numpy as np
from utils.ml_model import train_dummy_model
DB_PATH = 'db/analytics.sqlite'

def load_training_data(limit=10000):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT device_lat, device_lon, accuracy, addr_lat, addr_lon, corrected_lat, corrected_lon
        FROM corrections_history
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    X = []
    y = []
    for r in rows:
        device_lat, device_lon, accuracy, addr_lat, addr_lon, corr_lat, corr_lon = r
        feat = [device_lat, device_lon, accuracy, addr_lat, addr_lon]
        X.append(feat)
        y.append([corr_lat - device_lat, corr_lon - device_lon])
    if not X:
        return None, None
    return np.array(X), np.array(y)

def main():
    X, y = load_training_data()
    if X is None:
        print("Pas assez de données pour entraîner")
        return
    print("Training data loaded:", X.shape)
    model = train_dummy_model(X, y)
    print("Model trained and saved.")

if __name__ == '__main__':
    main()
