# server/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from server.models import GeocodeRequest, GPSPoint, RouteRequest
from server.utils.geocode import geocode, reverse_geocode
from server.utils.route import get_route
from server.utils.gps_advanced import compute_fusion, store_point, update_historical_offsets, compute_historical_bias, fetch_recent
from server.utils.analytics import stats_overall, heatmap_points, distance_by_device, problematic_zones
import time

app = FastAPI(title="GPS Precision + Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/validate-address")
def validate_address(req: GeocodeRequest):
    res = geocode(req.address)
    if not res:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"lat": res["lat"], "lon": res["lon"], "display_name": res["display_name"], "cached": res.get("cached", False)}

@app.post("/gps-correct")
def gps_correct(point: GPSPoint, address: GeocodeRequest = None):
    """
    Accepts device gps point and optional address to fuse.
    Returns corrected coordinates and stores history.
    """
    device = {"lat": point.lat, "lon": point.lon, "accuracy": point.accuracy}
    geocode_result = None
    if address:
        g = geocode(address.address)
        if g:
            geocode_result = {"lat": g["lat"], "lon": g["lon"]}
    if geocode_result:
        fusion = compute_fusion(device, geocode_result, device_accuracy=point.accuracy)
        corrected = {
            "device_id": point.device_id,
            "lat": point.lat,
            "lon": point.lon,
            "accuracy": point.accuracy,
            "timestamp": point.timestamp,
            "source": "fusion",
            "corrected_lat": fusion["corrected_lat"],
            "corrected_lon": fusion["corrected_lon"],
            "correction_reason": fusion["reason"]
        }
        store_point(corrected)
        update_historical_offsets(point.lat, point.lon, fusion["corrected_lat"], fusion["corrected_lon"])
        return {
            "corrected_lat": fusion["corrected_lat"],
            "corrected_lon": fusion["corrected_lon"],
            "used_weight_device": fusion["used_weight_device"],
            "used_weight_geocode": fusion["used_weight_geocode"],
            "reason": fusion["reason"]
        }
    else:
        # No geocode: possibly apply history bias
        bias = compute_historical_bias(point.lat, point.lon)
        if bias:
            corrected_lat = point.lat + bias["bias_lat"]
            corrected_lon = point.lon + bias["bias_lon"]
            reason = "historical_bias_applied"
        else:
            corrected_lat = point.lat
            corrected_lon = point.lon
            reason = "no_correction"
        corrected = {
            "device_id": point.device_id,
            "lat": point.lat,
            "lon": point.lon,
            "accuracy": point.accuracy,
            "timestamp": point.timestamp,
            "source": "device",
            "corrected_lat": corrected_lat,
            "corrected_lon": corrected_lon,
            "correction_reason": reason
        }
        store_point(corrected)
        return {
            "corrected_lat": corrected_lat,
            "corrected_lon": corrected_lon,
            "used_weight_device": 1.0,
            "used_weight_geocode": 0.0,
            "reason": reason
        }

@app.post("/get-optimized-route")
def optimized_route(req: RouteRequest):
    try:
        r = get_route(req.points, profile=req.profile)
        return r
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
def analytics(since: int = 0):
    meta = stats_overall(since)
    heat = heatmap_points(limit=2000)
    return {"meta": meta, "heatmap": heat}

@app.get("/analytics/device/{device_id}")
def analytics_device(device_id: str):
    d = distance_by_device(device_id)
    recent = fetch_recent(device_id, limit=100)
    return {"distance": d, "recent_points": recent}

@app.get("/analytics/problematic-zones")
def api_problematic_zones():
    zones = problematic_zones()
    return {"zones": zones}
