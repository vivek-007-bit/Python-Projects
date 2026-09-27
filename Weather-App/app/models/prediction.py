"""
Machine Learning Prediction Models and Schemas
"""

from typing import List, Optional, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.models.weather import HistoricalDataSummary


class HourlyPredictionItem(BaseModel):
    time: str = Field(..., description="Hour representation (e.g., '15:00')")
    datetime_iso: str
    temperature: float = Field(..., description="Predicted temperature in °C")
    humidity: int = Field(..., description="Predicted humidity percentage")
    rain_probability: float = Field(..., description="Estimated rain probability percentage (0-100)")
    condition_estimate: str = Field("Clear", description="Estimated condition summary")


class ModelEvaluationMetrics(BaseModel):
    temperature_mae: float = Field(..., description="Mean Absolute Error for Temperature (°C)")
    temperature_rmse: float = Field(..., description="Root Mean Squared Error for Temperature (°C)")
    humidity_mae: float = Field(..., description="Mean Absolute Error for Humidity (%)")
    humidity_rmse: float = Field(..., description="Root Mean Squared Error for Humidity (%)")
    rain_accuracy: float = Field(..., description="Classification Accuracy for Rain Prediction (0-1)")
    rain_precision: float = Field(..., description="Precision for Rain Prediction")
    rain_recall: float = Field(..., description="Recall for Rain Prediction")
    rain_f1: float = Field(..., description="F1 Score for Rain Prediction")
    train_samples: int = Field(..., description="Number of historical samples used for training")
    test_samples: int = Field(..., description="Number of historical samples used for evaluation")
    split_method: str = Field("Time-Series Chronological Split (80/20)", description="Validation split strategy")


class PredictionResult(BaseModel):
    rain_probability_next_24h: float = Field(..., description="Estimated probability of rain over next 24 hours (%)")
    rain_expected: bool = Field(..., description="Binary classification whether rain is predicted")
    rain_risk_level: str = Field("Low", description="Risk category: Low, Moderate, High, Very High")
    hourly_predictions: List[HourlyPredictionItem] = Field(..., description="Next 6 to 12 hours hourly predictions")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Key features contributing to prediction")
    evaluation: ModelEvaluationMetrics = Field(..., description="Metrics showing model performance on validation data")
    methodology_note: str = Field(
        "Lightweight time-series autoregressive regressors and ensemble classifier trained on location-specific 30-day historical observations.",
        description="Scientific explanation of model methodology"
    )


class PredictionBundleResponse(BaseModel):
    status: str = "success"
    prediction: PredictionResult
    historical: Dict = Field(..., description="Historical data summary dictionary")
