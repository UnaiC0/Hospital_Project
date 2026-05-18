"""Cargador e inferencia del modelo de triaje entrenado."""

import os
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np

try:
    import joblib
except ImportError:
    joblib = None


TRIAGE_MODEL_PATH = Path(os.getenv("TRIAGE_MODEL_PATH", "/models/triage_model.joblib"))
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("TRIAGE_LOW_CONFIDENCE", "0.55"))

_lock = Lock()
_artifact: dict[str, Any] | None = None
_load_error: str | None = None


def _try_load() -> None:
    global _artifact, _load_error
    if joblib is None:
        _load_error = "joblib no esta instalado"
        return
    if not TRIAGE_MODEL_PATH.exists():
        _load_error = f"artefacto no encontrado en {TRIAGE_MODEL_PATH}"
        return
    try:
        _artifact = joblib.load(TRIAGE_MODEL_PATH)
        _load_error = None
    except Exception as exc:
        _load_error = f"error al cargar modelo: {exc}"
        _artifact = None


def get_artifact() -> dict[str, Any] | None:
    global _artifact
    with _lock:
        if _artifact is None:
            file_missing_before = _load_error is not None and "no encontrado" in _load_error
            if _load_error is None or (file_missing_before and TRIAGE_MODEL_PATH.exists()):
                _try_load()
        return _artifact


def model_status() -> dict[str, Any]:
    artifact = get_artifact()
    if artifact is None:
        return {"loaded": False, "reason": _load_error or "no disponible"}
    return {
        "loaded": True,
        "model_name": artifact["model_name"],
        "model_version": artifact["model_version"],
        "path": str(TRIAGE_MODEL_PATH),
    }


def _vectorize(symptoms: list[str], vitals: dict[str, Any], artifact: dict[str, Any]) -> np.ndarray:
    sym_norm = {s.strip().lower() for s in symptoms if isinstance(s, str) and s.strip()}

    def num(key: str, default: float) -> float:
        value = vitals.get(key)
        if value is None or value == "":
            return float(default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    numeric_defaults = {
        "age": 45.0,
        "heart_rate": 80.0,
        "oxygen_saturation": 98.0,
        "systolic_bp": 120.0,
        "respiratory_rate": 16.0,
        "temperature": 36.8,
    }

    row: list[float] = []
    for feature in artifact["feature_order"]:
        if feature in numeric_defaults:
            row.append(num(feature, numeric_defaults[feature]))
        elif feature.startswith("symptom__"):
            symptom = feature.split("__", 1)[1]
            row.append(1.0 if symptom in sym_norm else 0.0)
        else:
            row.append(0.0)
    return np.array([row], dtype=np.float32)


def _top_contributors(
    vector: np.ndarray, artifact: dict[str, Any], top_k: int = 3
) -> list[dict[str, Any]]:
    importances = np.array(artifact.get("feature_importances", []), dtype=np.float64)
    if importances.size == 0:
        return []
    presence = (vector[0] != 0).astype(np.float64)
    contribution = importances * presence
    if contribution.sum() <= 0:
        contribution = importances
    order = np.argsort(contribution)[::-1][:top_k]
    feature_names = artifact["feature_order"]
    return [
        {
            "feature": feature_names[int(idx)],
            "importance": round(float(importances[int(idx)]), 4),
            "value": round(float(vector[0][int(idx)]), 2),
        }
        for idx in order
    ]


def predict(symptoms: list[str], vitals: dict[str, Any]) -> dict[str, Any] | None:
    artifact = get_artifact()
    if artifact is None:
        return None

    estimator = artifact["estimator"]
    labels: list[str] = artifact["risk_labels"]
    priority_map: dict[str, str] = artifact["priority_by_risk"]

    vector = _vectorize(symptoms, vitals, artifact)
    proba = estimator.predict_proba(vector)[0]
    pred_idx = int(np.argmax(proba))
    risk_level = labels[pred_idx]
    confidence = float(proba[pred_idx])
    probabilities = {label: round(float(p), 4) for label, p in zip(labels, proba)}

    score = int(round(confidence * 100 * (pred_idx + 1) / len(labels)))
    score = max(0, min(score, 100))

    contributors = _top_contributors(vector, artifact)
    alerts: list[str] = []
    if risk_level == "critical":
        alerts.append("Activar codigo de atencion inmediata.")
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        alerts.append("Confianza baja: validar con personal sanitario.")
    sym_norm = {s.strip().lower() for s in symptoms if isinstance(s, str)}
    if "chest pain" in sym_norm and risk_level in {"high", "critical"}:
        alerts.append("Dolor toracico con riesgo elevado: priorizar ECG.")

    return {
        "model_name": artifact["model_name"],
        "model_version": artifact["model_version"],
        "model_family": artifact.get("model_family", "random_forest"),
        "risk_level": risk_level,
        "recommended_priority": priority_map.get(risk_level, "standard"),
        "score": score,
        "confidence": round(confidence, 4),
        "probabilities": probabilities,
        "top_contributors": contributors,
        "alerts": alerts,
        "clinical_note": (
            "Salida del modelo de triaje. Apoyo a la decision clinica; "
            "no sustituye la valoracion del personal sanitario."
        ),
    }
