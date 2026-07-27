"""
Model Persistence
Save and load trained models with all required artefacts.
Every model save includes: model + scaler + feature list + metadata.
"""
import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

from ml.config.config import MODELS_DIR


def save_model(
    model_name: str,
    model: Any,
    feature_cols: list,
    scaler: Any = None,
    encoder: Any = None,
    metrics: Dict = None,
    extra_metadata: Dict = None,
) -> Path:
    """
    Save a trained model with all inference artefacts.
    Versioned by timestamp so rollback is always possible.
    
    Saves:
      {model_name}/
        model.joblib        ← trained model
        scaler.joblib       ← fitted scaler (if any)
        encoder.joblib      ← fitted encoder (if any)
        features.json       ← exact feature list used during training
        metadata.json       ← metrics + version + timestamp
    """
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = MODELS_DIR / model_name / version
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, model_dir / "model.joblib")
    
    # Save scaler if provided
    if scaler is not None:
        joblib.dump(scaler, model_dir / "scaler.joblib")
    
    # Save encoder if provided
    if encoder is not None:
        joblib.dump(encoder, model_dir / "encoder.joblib")
    
    # Save feature list
    with open(model_dir / "features.json", "w") as f:
        json.dump(feature_cols, f)
    
    # Save metadata
    metadata = {
        "model_name": model_name,
        "version": version,
        "trained_at": datetime.now().isoformat(),
        "feature_count": len(feature_cols),
        "metrics": metrics or {},
        **(extra_metadata or {}),
    }
    with open(model_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Write "latest" pointer so inference always finds current model
    latest_path = MODELS_DIR / model_name / "latest.txt"
    with open(latest_path, "w") as f:
        f.write(version)
    
    print(f"  💾 Saved {model_name} v{version} → {model_dir}")
    return model_dir


def load_model(model_name: str, version: str = None) -> Dict[str, Any]:
    """
    Load a saved model and all artefacts.
    
    Args:
        model_name: e.g. "spending_predictor"
        version: specific version string, or None for latest
    
    Returns:
        Dict with keys: model, scaler, encoder, features, metadata
    """
    model_base = MODELS_DIR / model_name
    
    if version is None:
        latest_file = model_base / "latest.txt"
        if not latest_file.exists():
            raise FileNotFoundError(f"No trained model found for '{model_name}'. Run training first.")
        version = latest_file.read_text().strip()
    
    model_dir = model_base / version
    
    result = {
        "model": joblib.load(model_dir / "model.joblib"),
        "scaler": joblib.load(model_dir / "scaler.joblib") if (model_dir / "scaler.joblib").exists() else None,
        "encoder": joblib.load(model_dir / "encoder.joblib") if (model_dir / "encoder.joblib").exists() else None,
        "features": json.load(open(model_dir / "features.json")),
        "metadata": json.load(open(model_dir / "metadata.json")),
        "version": version,
    }
    
    return result


def list_versions(model_name: str) -> list:
    """List all saved versions of a model."""
    model_base = MODELS_DIR / model_name
    if not model_base.exists():
        return []
    return sorted([d.name for d in model_base.iterdir() if d.is_dir()])


def get_model_info(model_name: str) -> Dict:
    """Get metadata of the latest version of a model."""
    try:
        artefacts = load_model(model_name)
        return {
            "model_name": model_name,
            "version": artefacts["version"],
            "metadata": artefacts["metadata"],
            "versions_available": list_versions(model_name),
        }
    except FileNotFoundError:
        return {"model_name": model_name, "status": "not trained"}
