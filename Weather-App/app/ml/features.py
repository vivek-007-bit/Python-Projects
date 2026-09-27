"""
Feature Engineering for Weather Prediction Models
Computes cyclical time signals, lag features, rolling aggregations, and meteorological indices.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple


def calculate_dew_point(temp_c: pd.Series, humidity_pct: pd.Series) -> pd.Series:
    """Approximate dew point temperature in Celsius."""
    return temp_c - ((100.0 - humidity_pct) / 5.0)


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Generate feature matrix from time-series DataFrame.
    Returns (DataFrame_with_features, feature_column_names).
    """
    data = df.copy()

    # 1. Cyclical Time Features
    hour = data["time"].dt.hour
    month = data["time"].dt.month
    day_of_week = data["time"].dt.dayofweek

    data["sin_hour"] = np.sin(2 * np.pi * hour / 24.0)
    data["cos_hour"] = np.cos(2 * np.pi * hour / 24.0)
    data["sin_month"] = np.sin(2 * np.pi * (month - 1) / 12.0)
    data["cos_month"] = np.cos(2 * np.pi * (month - 1) / 12.0)
    data["day_of_week"] = day_of_week

    # 2. Meteorological Derived Features
    data["dew_point"] = calculate_dew_point(data["temperature"], data["humidity"])
    
    # Wind vector components (U = East-West, V = North-South)
    wind_rad = np.deg2rad(data["wind_direction"].fillna(0))
    data["wind_u"] = -data["wind_speed"] * np.sin(wind_rad)
    data["wind_v"] = -data["wind_speed"] * np.cos(wind_rad)

    # 3. Time Lag Features (Past 1h, 2h, 3h, 6h)
    for lag in [1, 2, 3, 6]:
        data[f"temp_lag_{lag}h"] = data["temperature"].shift(lag)
        data[f"hum_lag_{lag}h"] = data["humidity"].shift(lag)
        data[f"press_lag_{lag}h"] = data["pressure"].shift(lag)
        data[f"precip_lag_{lag}h"] = data["precipitation"].shift(lag)

    # 4. Rolling Window Features (6h, 24h)
    data["temp_roll_mean_6h"] = data["temperature"].rolling(window=6, min_periods=1).mean()
    data["temp_roll_std_6h"] = data["temperature"].rolling(window=6, min_periods=1).std().fillna(0)
    data["temp_roll_mean_24h"] = data["temperature"].rolling(window=24, min_periods=1).mean()

    data["hum_roll_mean_6h"] = data["humidity"].rolling(window=6, min_periods=1).mean()
    data["hum_roll_mean_24h"] = data["humidity"].rolling(window=24, min_periods=1).mean()

    # Barometric pressure trend (3-hour change: critical indicator for incoming weather fronts)
    data["press_trend_3h"] = data["pressure"] - data["pressure"].shift(3)

    # Precipitation accumulation over past 24 hours
    data["precip_accum_24h"] = data["precipitation"].rolling(window=24, min_periods=1).sum()

    # Feature column definitions
    feature_cols = [
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "dew_point",
        "wind_u",
        "wind_v",
        "sin_hour",
        "cos_hour",
        "sin_month",
        "cos_month",
        "day_of_week",
        "temp_lag_1h",
        "temp_lag_2h",
        "temp_lag_3h",
        "temp_lag_6h",
        "hum_lag_1h",
        "hum_lag_2h",
        "hum_lag_3h",
        "hum_lag_6h",
        "press_lag_1h",
        "press_lag_3h",
        "precip_lag_1h",
        "temp_roll_mean_6h",
        "temp_roll_std_6h",
        "temp_roll_mean_24h",
        "hum_roll_mean_6h",
        "hum_roll_mean_24h",
        "press_trend_3h",
        "precip_accum_24h"
    ]

    # Fill any NaN caused by shifting using backward fill
    data[feature_cols] = data[feature_cols].bfill().ffill()

    return data, feature_cols
