# server/models.py
from pydantic import BaseModel, Field
from typing import Optional, List

class GeocodeRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    lat: float
    lon: float
    display_name: str

class GPSPoint(BaseModel):
    device_id: str
    lat: float
    lon: float
    accuracy: Optional[float] = Field(None, description="Reported GPS accuracy in meters")
    timestamp: int
    source: Optional[str] = "device"  # device|geocode|fusion

class GPSCorrectResponse(BaseModel):
    corrected_lat: float
    corrected_lon: float
    used_weight_device: float
    used_weight_geocode: float
    reason: str

class RouteRequest(BaseModel):
    points: List[List[float]]  # [[lon, lat], [lon, lat], ...] (OSRM expects lon,lat)
    profile: Optional[str] = "driving"

class RouteResponse(BaseModel):
    distance: float
    duration: float
    geometry: str
