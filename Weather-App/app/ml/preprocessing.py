"""
Data Preprocessing for Chronological Weather Time-Series
"""

import pandas as pd
import numpy as np
from typing import Tuple


def clean_and_prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, validate, and prepare raw historical weather data.
    Ensures chronological ordering, handles missing data, and defines targets.
    """
    if df.empty or len(df) < 48:
        raise ValueError(f"Insufficient historical data points: {len(df)}. Minimum 48 required.")

    # Sort strictly by time
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["time"]):
        df["time"] = pd.to_datetime(df["time"])
    
    df = df.sort_values("time").reset_index(drop=True)

    # Clean numeric columns
    numeric_cols = ["temperature", "humidity", "pressure", "precipitation", "rain", "wind_speed", "wind_direction"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Forward fill then backward fill any gaps
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    # Constrain physical limits
    df["humidity"] = df["humidity"].clip(0, 100)
    df["precipitation"] = df["precipitation"].clip(lower=0.0)
    df["rain"] = df["rain"].clip(lower=0.0)
    df["wind_speed"] = df["wind_speed"].clip(lower=0.0)

    # 1. Target for Rain in Next 24 Hours (Binary Classification)
    # Precipitation sum over the forward 24-hour window > 0.2 mm
    rolling_forward_precip = df["precipitation"].iloc[::-1].rolling(window=24, min_periods=1).sum().iloc[::-1]
    df["target_rain_next_24h"] = (rolling_forward_precip > 0.2).astype(int)

    # 2. Targets for Multi-step hourly temperature & humidity (Horizons: +1h, +2h, +3h, +4h, +5h, +6h)
    for h in range(1, 7):
        df[f"target_temp_h{h}"] = df["temperature"].shift(-h)
        df[f"target_hum_h{h}"] = df["humidity"].shift(-h)

    return df
