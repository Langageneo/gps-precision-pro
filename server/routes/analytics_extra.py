from fastapi import APIRouter
from utils import analytics, alerts, scores

router = APIRouter(prefix="/analytics_extra", tags=["analytics_extra"])

@router.get("/livreurs/scores")
async def livreurs_scores():
    return scores.compute_driver_scores()

@router.get("/livreurs/best")
async def livreur_best():
    return scores.get_best_driver()

@router.get("/alerts")
async def get_alerts():
    return alerts.generate_alerts()
