"""
Model Evaluation and Metrics Utility
Provides standalone helpers for validating time-series predictions.
"""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, precision_score, recall_score, f1_score


def evaluate_time_series_models(
    y_temp_true: np.ndarray,
    y_temp_pred: np.ndarray,
    y_hum_true: np.ndarray,
    y_hum_pred: np.ndarray,
    y_rain_true: np.ndarray,
    y_rain_pred: np.ndarray
) -> Dict[str, float]:
    """Calculate summary regression and classification evaluation metrics."""
    return {
        "temperature_mae": round(float(mean_absolute_error(y_temp_true, y_temp_pred)), 2),
        "temperature_rmse": round(float(np.sqrt(mean_squared_error(y_temp_true, y_temp_pred))), 2),
        "humidity_mae": round(float(mean_absolute_error(y_hum_true, y_hum_pred)), 2),
        "humidity_rmse": round(float(np.sqrt(mean_squared_error(y_hum_true, y_hum_pred))), 2),
        "rain_accuracy": round(float(accuracy_score(y_rain_true, y_rain_pred)), 3),
        "rain_precision": round(float(precision_score(y_rain_true, y_rain_pred, zero_division=0)), 3),
        "rain_recall": round(float(recall_score(y_rain_true, y_rain_pred, zero_division=0)), 3),
        "rain_f1": round(float(f1_score(y_rain_true, y_rain_pred, zero_division=0)), 3),
    }
