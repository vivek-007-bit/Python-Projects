"""
Machine Learning Pipeline for Weather Prediction
Trains location-specific classification & regression models on demand.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, precision_score, recall_score, f1_score

from app.config import settings
from app.ml.preprocessing import clean_and_prepare_dataset
from app.ml.features import engineer_features
from app.models.prediction import (
    PredictionResult,
    ModelEvaluationMetrics,
    HourlyPredictionItem
)

logger = logging.getLogger(__name__)


class WeatherMLPipeline:
    def __init__(self):
        self.n_estimators = settings.ML_N_ESTIMATORS
        self.random_state = settings.ML_RANDOM_STATE

    def train_and_predict(self, raw_df: pd.DataFrame) -> PredictionResult:
        """
        Execute full ML pipeline:
        1. Clean and engineer features.
        2. Perform chronological time-series evaluation.
        3. Train rain classifier and multi-horizon temperature/humidity regressors.
        4. Generate next 6-hour predictions and rain risk evaluation.
        """
        # Step 1: Preprocess and engineer features
        df_clean = clean_and_prepare_dataset(raw_df)
        df_feat, feature_cols = engineer_features(df_clean)

        # Drop rows where multi-step targets are NaN (the final 6 rows)
        valid_mask = df_feat["target_temp_h6"].notna() & df_feat["target_rain_next_24h"].notna()
        dataset = df_feat[valid_mask].copy()

        if len(dataset) < 40:
            raise ValueError("Insufficient valid samples after feature engineering.")

        # Step 2: Chronological Split (80% Train, 20% Test)
        split_idx = int(len(dataset) * 0.8)
        train_data = dataset.iloc[:split_idx]
        test_data = dataset.iloc[split_idx:]

        X_train = train_data[feature_cols]
        X_test = test_data[feature_cols]

        # Targets
        y_rain_train = train_data["target_rain_next_24h"]
        y_rain_test = test_data["target_rain_next_24h"]

        # Step 3: Train & Evaluate Rain Classifier
        rain_clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=6,
            min_samples_split=4,
            random_state=self.random_state,
            class_weight="balanced"
        )
        rain_clf.fit(X_train, y_rain_train)
        rain_pred = rain_clf.predict(X_test)

        rain_acc = float(accuracy_score(y_rain_test, rain_pred))
        rain_prec = float(precision_score(y_rain_test, rain_pred, zero_division=0))
        rain_rec = float(recall_score(y_rain_test, rain_pred, zero_division=0))
        rain_f1 = float(f1_score(y_rain_test, rain_pred, zero_division=0))

        # Step 4: Train & Evaluate Temperature & Humidity Regressors (Horizons 1 to 6)
        temp_models: Dict[int, RandomForestRegressor] = {}
        hum_models: Dict[int, RandomForestRegressor] = {}
        
        temp_maes, temp_rmses = [], []
        hum_maes, hum_rmses = [], []

        for h in range(1, 7):
            # Temp regressor
            y_temp_train = train_data[f"target_temp_h{h}"]
            y_temp_test = test_data[f"target_temp_h{h}"]
            
            t_model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=6,
                random_state=self.random_state
            )
            t_model.fit(X_train, y_temp_train)
            t_pred = t_model.predict(X_test)
            
            temp_models[h] = t_model
            temp_maes.append(mean_absolute_error(y_temp_test, t_pred))
            temp_rmses.append(np.sqrt(mean_squared_error(y_temp_test, t_pred)))

            # Humidity regressor
            y_hum_train = train_data[f"target_hum_h{h}"]
            y_hum_test = test_data[f"target_hum_h{h}"]
            
            h_model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=6,
                random_state=self.random_state
            )
            h_model.fit(X_train, y_hum_train)
            h_pred = h_model.predict(X_test)
            
            hum_models[h] = h_model
            hum_maes.append(mean_absolute_error(y_hum_test, h_pred))
            hum_rmses.append(np.sqrt(mean_squared_error(y_hum_test, h_pred)))

        eval_metrics = ModelEvaluationMetrics(
            temperature_mae=round(float(np.mean(temp_maes)), 2),
            temperature_rmse=round(float(np.mean(temp_rmses)), 2),
            humidity_mae=round(float(np.mean(hum_maes)), 2),
            humidity_rmse=round(float(np.mean(hum_rmses)), 2),
            rain_accuracy=round(rain_acc, 3),
            rain_precision=round(rain_prec, 3),
            rain_recall=round(rain_rec, 3),
            rain_f1=round(rain_f1, 3),
            train_samples=len(train_data),
            test_samples=len(test_data),
            split_method="Time-Series Chronological Split (80% Train / 20% Test)"
        )

        # Step 5: Feature Importances
        importances = rain_clf.feature_importances_
        top_indices = np.argsort(importances)[::-1][:5]
        top_features = {feature_cols[i]: round(float(importances[i]), 3) for i in top_indices}

        # Step 6: Generate Predictions for the upcoming hours using the latest observation
        latest_row = df_feat.iloc[[-1]][feature_cols]
        
        # Predict Rain Probability
        if hasattr(rain_clf, "predict_proba"):
            rain_prob_classes = rain_clf.predict_proba(latest_row)[0]
            # Prob of class 1 (Rain)
            rain_prob = float(rain_prob_classes[1] * 100.0) if len(rain_prob_classes) > 1 else 0.0
        else:
            rain_prob = float(rain_clf.predict(latest_row)[0] * 100.0)

        rain_prob = round(min(max(rain_prob, 0.0), 100.0), 1)
        rain_expected = rain_prob >= 50.0

        if rain_prob < 20:
            risk_level = "Low"
        elif rain_prob < 50:
            risk_level = "Moderate"
        elif rain_prob < 80:
            risk_level = "High"
        else:
            risk_level = "Very High"

        # Generate 6-hour future hourly predictions
        latest_time = df_clean["time"].iloc[-1]
        hourly_predictions: List[HourlyPredictionItem] = []

        for h in range(1, 7):
            target_dt = latest_time + timedelta(hours=h)
            pred_temp = float(temp_models[h].predict(latest_row)[0])
            pred_hum = int(np.clip(round(hum_models[h].predict(latest_row)[0]), 0, 100))
            
            # Simple condition estimation based on predicted humidity & temperature
            if rain_prob > 60 and pred_hum > 75:
                cond_est = "Rainy"
            elif pred_hum > 70:
                cond_est = "Cloudy"
            elif pred_temp > 28:
                cond_est = "Warm / Clear"
            else:
                cond_est = "Clear"

            hourly_predictions.append(
                HourlyPredictionItem(
                    time=target_dt.strftime("%H:00"),
                    datetime_iso=target_dt.isoformat(),
                    temperature=round(pred_temp, 1),
                    humidity=pred_hum,
                    rain_probability=round(min(rain_prob * (0.8 + 0.05 * h), 100.0), 1),
                    condition_estimate=cond_est
                )
            )

        return PredictionResult(
            rain_probability_next_24h=rain_prob,
            rain_expected=rain_expected,
            rain_risk_level=risk_level,
            hourly_predictions=hourly_predictions,
            feature_importance=top_features,
            evaluation=eval_metrics,
            methodology_note=(
                "Models are dynamically trained on the past 30 days of chronological hourly observations "
                "specific to this location using Scikit-Learn Random Forests with lag and rolling features."
            )
        )


ml_pipeline = WeatherMLPipeline()
