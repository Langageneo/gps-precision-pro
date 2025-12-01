# server/config.py
import os

# Services endpoints
NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
NOMINATIM_REVERSE = os.getenv("NOMINATIM_REVERSE", "https://nominatim.openstreetmap.org/reverse")
OSRM_URL = os.getenv("OSRM_URL", "http://router.project-osrm.org")  # OSRM public
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./server/analytics.sqlite")
APP_NAME = "GPS Precision + Analytics API"
