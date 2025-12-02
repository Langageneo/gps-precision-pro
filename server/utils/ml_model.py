import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = 'server/ai/model_gps_bias.pkl'

def train_dummy_model(X, y):
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def predict_bias(features):
    """
    features: 2D array-like (n_samples, n_features)
    returns predicted bias (lat_bias, lon_bias) per sample or zeros if no model
    """
    model = load_model()
    if model is None:
        # fallback tiny random noise
        return np.zeros((len(features), 2)).tolist()
    preds = model.predict(features)
    # assume model returns 2 values per sample packed; if single-output adapt
    return preds.tolist()
