"""
Test Suite for Machine Learning Pipeline, Features, and Predictions
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.ml.preprocessing import clean_and_prepare_dataset
from app.ml.features import engineer_features
from app.ml.models import WeatherMLPipeline
from app.models.prediction import PredictionResult


@pytest.fixture
def sample_raw_weather_df():
    """Generate 720 hours (30 days) of synthetic yet realistic chronological weather observations for testing."""
    np.random.seed(42)
    n_hours = 720
    start_time = datetime(2026, 1, 1, 0, 0)
    times = [start_time + timedelta(hours=i) for i in range(n_hours)]
    
    # Diurnal temperature cycle with noise
    hours = np.array([t.hour for t in times])
    base_temp = 22.0 + 8.0 * np.sin(2 * np.pi * (hours - 9) / 24.0) + np.random.normal(0, 1.5, n_hours)
    
    # Humidity negatively correlated with temperature
    base_hum = np.clip(80.0 - 25.0 * np.sin(2 * np.pi * (hours - 9) / 24.0) + np.random.normal(0, 5.0, n_hours), 10, 100)
    
    # Pressure with slow fluctuation
    base_press = 1013.0 + 5.0 * np.sin(2 * np.pi * np.arange(n_hours) / 120.0) + np.random.normal(0, 1.0, n_hours)
    
    # Occasional rain
    rain_mask = (base_hum > 75) & (np.random.uniform(0, 1, n_hours) > 0.6)
    precipitation = np.where(rain_mask, np.random.exponential(2.5, n_hours), 0.0)
    
    wind_speed = np.abs(np.random.normal(3.5, 1.5, n_hours))
    wind_dir = np.random.uniform(0, 360, n_hours)
    cloud_cover = np.clip(base_hum * 0.8 + np.random.normal(0, 10, n_hours), 0, 100)
    
    return pd.DataFrame({
        "time": times,
        "temperature": base_temp,
        "humidity": base_hum,
        "pressure": base_press,
        "precipitation": precipitation,
        "rain": precipitation,
        "wind_speed": wind_speed,
        "wind_direction": wind_dir,
        "cloud_cover": cloud_cover,
        "weather_code": np.zeros(n_hours)
    })


def test_clean_and_prepare_dataset(sample_raw_weather_df):
    df_clean = clean_and_prepare_dataset(sample_raw_weather_df)
    
    assert len(df_clean) == len(sample_raw_weather_df)
    assert "target_rain_next_24h" in df_clean.columns
    assert "target_temp_h1" in df_clean.columns
    assert "target_temp_h6" in df_clean.columns
    assert "target_hum_h1" in df_clean.columns
    assert "target_hum_h6" in df_clean.columns
    assert df_clean["humidity"].min() >= 0
    assert df_clean["humidity"].max() <= 100


def test_engineer_features(sample_raw_weather_df):
    df_clean = clean_and_prepare_dataset(sample_raw_weather_df)
    df_feat, feature_cols = engineer_features(df_clean)
    
    assert len(feature_cols) > 15
    for col in feature_cols:
        assert col in df_feat.columns
        assert not df_feat[col].isna().any(), f"Feature column {col} contains NaN values"
    
    assert "sin_hour" in feature_cols
    assert "cos_hour" in feature_cols
    assert "temp_lag_1h" in feature_cols
    assert "press_trend_3h" in feature_cols


def test_ml_pipeline_train_and_predict(sample_raw_weather_df):
    pipeline = WeatherMLPipeline()
    result = pipeline.train_and_predict(sample_raw_weather_df)
    
    assert isinstance(result, PredictionResult)
    assert 0.0 <= result.rain_probability_next_24h <= 100.0
    assert result.rain_risk_level in ["Low", "Moderate", "High", "Very High"]
    assert len(result.hourly_predictions) == 6
    
    # Check evaluation metrics
    assert result.evaluation.temperature_mae >= 0.0
    assert result.evaluation.humidity_mae >= 0.0
    assert 0.0 <= result.evaluation.rain_accuracy <= 1.0
    assert result.evaluation.train_samples > 0
    assert result.evaluation.test_samples > 0
