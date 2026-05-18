import json
import os
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models"))
RANDOM_STATE = int(os.getenv("TRIAGE_RANDOM_STATE", "42"))
N_SAMPLES = int(os.getenv("TRIAGE_SAMPLES", "8000"))
N_ESTIMATORS = int(os.getenv("TRIAGE_N_ESTIMATORS", "400"))
MAX_DEPTH = int(os.getenv("TRIAGE_MAX_DEPTH", "12"))
NOISE_RATE = float(os.getenv("TRIAGE_NOISE_RATE", "0.06"))

RISK_LABELS = ["low", "medium", "high", "critical"]
PRIORITY_BY_RISK = {
    "low": "standard",
    "medium": "priority",
    "high": "urgent",
    "critical": "immediate",
}

SYMPTOMS = [
    "chest pain",
    "shortness of breath",
    "loss of consciousness",
    "fever",
    "cough",
    "abdominal pain",
    "headache",
    "dizziness",
    "vomiting",
    "bleeding",
]

NUMERIC_FEATURES = [
    "age",
    "heart_rate",
    "oxygen_saturation",
    "systolic_bp",
    "respiratory_rate",
    "temperature",
]
FEATURE_ORDER = NUMERIC_FEATURES + [f"symptom__{s}" for s in SYMPTOMS]


def _news2_score(row: dict) -> int:
    """Aproximacion del National Early Warning Score 2."""
    score = 0
    rr = row["respiratory_rate"]
    if rr <= 8:
        score += 3
    elif rr <= 11:
        score += 1
    elif rr >= 25:
        score += 3
    elif rr >= 21:
        score += 2

    spo2 = row["oxygen_saturation"]
    if spo2 <= 91:
        score += 3
    elif spo2 <= 93:
        score += 2
    elif spo2 <= 95:
        score += 1

    sbp = row["systolic_bp"]
    if sbp <= 90:
        score += 3
    elif sbp <= 100:
        score += 2
    elif sbp <= 110:
        score += 1
    elif sbp >= 220:
        score += 3

    hr = row["heart_rate"]
    if hr <= 40:
        score += 3
    elif hr <= 50:
        score += 1
    elif hr >= 131:
        score += 3
    elif hr >= 111:
        score += 2
    elif hr >= 91:
        score += 1

    temp = row["temperature"]
    if temp <= 35.0:
        score += 3
    elif temp <= 36.0:
        score += 1
    elif temp >= 39.1:
        score += 2
    elif temp >= 38.1:
        score += 1

    return score


def _generate_sample(rng: np.random.Generator) -> dict:
    age = float(rng.integers(low=1, high=98))
    heart_rate = float(np.clip(rng.normal(85, 22), 35, 200))
    oxygen_saturation = float(np.clip(rng.normal(96, 4), 70, 100))
    systolic_bp = float(np.clip(rng.normal(125, 22), 60, 220))
    respiratory_rate = float(np.clip(rng.normal(17, 5), 6, 40))
    temperature = float(np.clip(rng.normal(37.0, 0.9), 34.5, 41.0))

    sample = {
        "age": age,
        "heart_rate": heart_rate,
        "oxygen_saturation": oxygen_saturation,
        "systolic_bp": systolic_bp,
        "respiratory_rate": respiratory_rate,
        "temperature": temperature,
    }

    red_flags = {"chest pain", "shortness of breath", "loss of consciousness", "bleeding"}
    n_symptoms = int(rng.integers(low=0, high=5))
    chosen = list(rng.choice(SYMPTOMS, size=n_symptoms, replace=False)) if n_symptoms else []
    for s in SYMPTOMS:
        sample[f"symptom__{s}"] = 1 if s in chosen else 0

    news2 = _news2_score(sample)
    red_flag_count = sum(1 for s in chosen if s in red_flags)

    severity = news2 + red_flag_count * 2 + (1 if age >= 75 else 0)

    if severity >= 9 or red_flag_count >= 2 or oxygen_saturation <= 88:
        label = "critical"
    elif severity >= 6:
        label = "high"
    elif severity >= 3:
        label = "medium"
    else:
        label = "low"

    sample["__label"] = label
    return sample


def build_dataset(n_samples: int, noise_rate: float, seed: int):
    rng = np.random.default_rng(seed)
    rows = [_generate_sample(rng) for _ in range(n_samples)]

    X = np.array([[r[f] for f in FEATURE_ORDER] for r in rows], dtype=np.float32)
    y_text = np.array([r["__label"] for r in rows])

    if noise_rate > 0:
        flip_mask = rng.random(size=len(y_text)) < noise_rate
        for i in np.where(flip_mask)[0]:
            current_idx = RISK_LABELS.index(y_text[i])
            shift = int(rng.choice([-1, 1]))
            new_idx = max(0, min(len(RISK_LABELS) - 1, current_idx + shift))
            y_text[i] = RISK_LABELS[new_idx]

    y = np.array([RISK_LABELS.index(label) for label in y_text], dtype=np.int64)
    return X, y


def train_and_save() -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    started = perf_counter()

    X, y = build_dataset(N_SAMPLES, NOISE_RATE, RANDOM_STATE)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    base = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    base.fit(X_train, y_train)

    calibrated = CalibratedClassifierCV(base, method="isotonic", cv=5)
    calibrated.fit(X_train, y_train)

    y_pred = calibrated.predict(X_test)
    accuracy = float((y_pred == y_test).mean())
    report = classification_report(
        y_test, y_pred, target_names=RISK_LABELS, output_dict=True, zero_division=0
    )
    matrix = confusion_matrix(y_test, y_pred, labels=list(range(len(RISK_LABELS)))).tolist()
    importances = base.feature_importances_.tolist()

    artifact = {
        "model_name": "hospital-triage-rf-calibrated",
        "model_version": "1.0.0",
        "model_family": "random_forest_isotonic_calibration",
        "risk_labels": RISK_LABELS,
        "priority_by_risk": PRIORITY_BY_RISK,
        "feature_order": FEATURE_ORDER,
        "numeric_features": NUMERIC_FEATURES,
        "symptom_features": SYMPTOMS,
        "estimator": calibrated,
        "feature_importances": importances,
    }
    model_path = MODEL_DIR / "triage_model.joblib"
    joblib.dump(artifact, model_path)

    metrics = {
        "model": artifact["model_name"],
        "version": artifact["model_version"],
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "duration_seconds": round(perf_counter() - started, 2),
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix": matrix,
        "labels_order": RISK_LABELS,
        "feature_importances": dict(zip(FEATURE_ORDER, importances)),
        "synthetic_basis": "MEWS/NEWS2-inspired rules with label noise",
        "clinical_reading_hint": (
            "Atender especialmente al recall de la clase 'critical' y a los"
            " falsos negativos de SpO2 baja o sintomas red-flag."
        ),
    }
    (MODEL_DIR / "triage_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: v for k, v in metrics.items() if k != "classification_report"}, indent=2))
    return metrics


if __name__ == "__main__":
    train_and_save()
