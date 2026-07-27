"""
Module 8 – Prediction Service Layer
The only file that API routes should call.
Handles: model loading, feature preparation, inference, explanation.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from ml.inference.persistence import load_model, get_model_info
from ml.recommendation.engine import get_recommendations


class PredictionService:
    """
    Loads all trained models once and serves predictions.
    Stateless — safe for FastAPI's dependency injection.
    """

    # ─────────────────────────────────────────
    # Spending Prediction
    # ─────────────────────────────────────────

    def predict_spending(self, user_features: Dict) -> Dict:
        """
        Predict the next transaction amount.
        
        Args:
            user_features: dict of feature values from user's recent transactions
        
        Returns:
            prediction, confidence range, feature explanation
        """
        try:
            artefacts = load_model("spending_predictor")
        except FileNotFoundError:
            return {"error": "Model not trained yet. Run training pipeline first."}

        model = artefacts["model"]
        scaler = artefacts["scaler"]
        features = artefacts["features"]
        metadata = artefacts["metadata"]

        # Build feature vector — fill missing with 0
        X = pd.DataFrame([{f: user_features.get(f, 0) for f in features}])

        # Scale if needed (linear models require scaling)
        algo = metadata.get("algorithm", "")
        if algo in ["LinearRegression", "Ridge", "Lasso"] and scaler:
            X_input = scaler.transform(X)
        else:
            X_input = X.values

        prediction = float(model.predict(X_input)[0])
        prediction = max(prediction, 0)  # spending can't be negative

        # Feature importance explanation
        explanation = self._explain_regression(model, X, features, algo)

        return {
            "predicted_amount": round(prediction, 2),
            "currency": "INR",
            "model_version": artefacts["version"],
            "algorithm": algo,
            "explanation": explanation,
            "model_metrics": metadata.get("metrics", {}),
        }

    # ─────────────────────────────────────────
    # Cash Exhaustion
    # ─────────────────────────────────────────

    def predict_cash_exhaustion(self, user_features: Dict) -> Dict:
        """
        Predict days until balance drops below threshold and 30-day risk.
        """
        result = {}

        # Days prediction
        try:
            reg_art = load_model("cash_exhaustion_regressor")
            model_reg = reg_art["model"]
            features_reg = reg_art["features"]
            X_reg = pd.DataFrame([{f: user_features.get(f, 0) for f in features_reg}])
            days = float(model_reg.predict(X_reg)[0])
            days = max(0, days)
            result["days_until_low_balance"] = round(days, 1)
            result["threshold"] = reg_art["metadata"].get("threshold", 1000)
            result["regressor_version"] = reg_art["version"]
        except FileNotFoundError:
            result["days_until_low_balance"] = None
            result["error"] = "Cash exhaustion model not trained yet."

        # Risk classification
        try:
            clf_art = load_model("cash_exhaustion_classifier")
            model_clf = clf_art["model"]
            features_clf = clf_art["features"]
            X_clf = pd.DataFrame([{f: user_features.get(f, 0) for f in features_clf}])
            risk = int(model_clf.predict(X_clf)[0])
            proba = model_clf.predict_proba(X_clf)[0]
            result["low_balance_risk"] = risk
            result["risk_probability"] = round(float(proba[1]), 3)
        except FileNotFoundError:
            result["low_balance_risk"] = None

        return result

    # ─────────────────────────────────────────
    # Anomaly Detection
    # ─────────────────────────────────────────

    def detect_anomaly(self, transaction_features: Dict) -> Dict:
        """
        Determine if a single transaction is anomalous.
        """
        try:
            artefacts = load_model("anomaly_detector")
        except FileNotFoundError:
            return {"error": "Anomaly model not trained yet."}

        model = artefacts["model"]
        scaler = artefacts["scaler"]
        features = artefacts["features"]

        X = pd.DataFrame([{f: transaction_features.get(f, 0) for f in features}])
        X_scaled = scaler.transform(X)

        label = int(model.predict(X_scaled)[0])           # -1=anomaly, 1=normal
        score = float(model.score_samples(X_scaled)[0])   # lower = more anomalous

        is_anomaly = label == -1

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "interpretation": (
                "This transaction is unusual compared to your spending history."
                if is_anomaly else
                "This transaction is within your normal spending pattern."
            ),
            "model_version": artefacts["version"],
        }

    # ─────────────────────────────────────────
    # User Segmentation
    # ─────────────────────────────────────────

    def get_user_segment(self, user_features: Dict) -> Dict:
        """Return user's spending personality cluster."""
        segment_names = {
            0: "Conservative Saver",
            1: "Balanced Spender",
            2: "Heavy Spender",
            3: "Frequent Micro-Spender",
            4: "Luxury Buyer",
        }
        segment_descriptions = {
            0: "You spend conservatively and save well.",
            1: "Your spending is balanced across categories.",
            2: "Your spending is above average. Consider budgeting.",
            3: "You make many small transactions frequently.",
            4: "You tend to make high-value purchases.",
        }

        try:
            artefacts = load_model("user_segmentation")
        except FileNotFoundError:
            return {"error": "Segmentation model not trained yet."}

        model = artefacts["model"]
        scaler = artefacts["scaler"]
        features = artefacts["features"]

        X = pd.DataFrame([{f: user_features.get(f, 0) for f in features}])
        X_scaled = scaler.transform(X)
        cluster = int(model.predict(X_scaled)[0])

        return {
            "cluster_id": cluster,
            "segment": segment_names.get(cluster, f"Segment {cluster}"),
            "description": segment_descriptions.get(cluster, ""),
            "model_version": artefacts["version"],
        }

    # ─────────────────────────────────────────
    # Recommendations
    # ─────────────────────────────────────────

    def get_recommendations(
        self,
        user_stats: Dict,
        user_features: Dict = None,
    ) -> Dict:
        """
        Generate personalised recommendations using all available model outputs.
        """
        user_features = user_features or {}

        # Run all models to gather signals
        exhaustion = {}
        anomaly = {}
        cluster_label = None

        if user_features:
            try:
                exhaustion = self.predict_cash_exhaustion(user_features)
            except Exception:
                pass

            try:
                segment = self.get_user_segment(user_features)
                cluster_label = segment.get("cluster_id")
            except Exception:
                pass

        recs = get_recommendations(
            user_stats=user_stats,
            anomaly_results=anomaly,
            cash_exhaustion=exhaustion,
            cluster_label=cluster_label,
        )

        return {
            "total_recommendations": len(recs),
            "recommendations": recs,
        }

    # ─────────────────────────────────────────
    # Model Info
    # ─────────────────────────────────────────

    def get_all_model_info(self) -> Dict:
        models = [
            "spending_predictor",
            "cash_exhaustion_regressor",
            "cash_exhaustion_classifier",
            "anomaly_detector",
            "user_segmentation",
        ]
        return {name: get_model_info(name) for name in models}

    # ─────────────────────────────────────────
    # Explanation Helper
    # ─────────────────────────────────────────

    def _explain_regression(self, model, X: pd.DataFrame, features: list, algo: str) -> Dict:
        """
        Extract feature importance for explainability.
        Linear models → coefficients. Tree models → feature_importances_.
        """
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                top_idx = np.argsort(importances)[::-1][:5]
                return {
                    "type": "feature_importance",
                    "top_features": [
                        {"feature": features[i], "importance": round(float(importances[i]), 4)}
                        for i in top_idx
                    ]
                }
            elif hasattr(model, "coef_"):
                coefs = model.coef_.flatten()
                top_idx = np.argsort(np.abs(coefs))[::-1][:5]
                return {
                    "type": "coefficients",
                    "top_features": [
                        {"feature": features[i], "coefficient": round(float(coefs[i]), 4)}
                        for i in top_idx
                    ]
                }
        except Exception:
            pass
        return {}


# Singleton — one instance loaded once per server process
prediction_service = PredictionService()
