"""
API Route for Machine Learning Prediction Engine
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.prediction import PredictionBundleResponse
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/prediction", tags=["prediction"])


@router.get("", response_model=PredictionBundleResponse)
async def get_prediction(
    lat: float = Query(..., description="Geographical latitude"),
    lon: float = Query(..., description="Geographical longitude")
):
    """
    Generate location-specific machine learning predictions (precipitation risk, 6h forecast,
    and historical statistics) based on real 30-day historical weather observations.
    """
    try:
        return await weather_service.get_prediction_bundle(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML prediction pipeline failed: {str(e)}")
