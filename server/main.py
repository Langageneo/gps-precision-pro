from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import analytics, geocode, gps_advanced, route

app = FastAPI(title="GPS Precision API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production : restreindre
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints existants
@app.get("/validate-address")
async def validate_address(address: str):
    return geocode.geocode_address(address)

@app.get("/gps-correct")
async def gps_correct(lat: float, lon: float, device_accuracy: float):
    return gps_advanced.correct_gps(lat, lon, device_accuracy)

@app.get("/get-optimized-route")
async def get_optimized_route(start: str, end: str):
    return route.get_route(start, end)

# Nouveaux endpoints Analytics
@app.get("/analytics")
async def get_analytics():
    return analytics.get_all_stats()

@app.get("/analytics/livreurs")
async def get_livreurs():
    return analytics.get_livreurs_stats()

@app.get("/analytics/meilleur-livreur")
async def meilleur_livreur():
    return analytics.get_best_livreur()

@app.get("/analytics/produits-populaires")
async def produits_populaires(top_n: int = 10):
    return analytics.get_popular_products(top_n)

@app.get("/analytics/heatmap-zones")
async def heatmap_zones():
    return analytics.get_heatmap_zones()

@app.get("/analytics/alertes")
async def alertes():
    return analytics.get_alerts()

@app.get("/analytics/predictive")
async def predictive():
    return analytics.predictive_suggestions()
