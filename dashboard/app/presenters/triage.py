from __future__ import annotations

from typing import Any

from app.triage.catalog import (
    TRIAGE_PRIORITY_DISPLAY,
    TRIAGE_RISK_DISPLAY,
    TRIAGE_RISK_LABELS,
)


def build_triage_result(data: dict) -> dict:
    risk = str(data.get("risk_level", "")).lower()
    priority = str(data.get("recommended_priority", "")).lower()

    try:
        confidence_pct = round(float(data.get("confidence") or 0.0) * 100, 1)
    except (TypeError, ValueError):
        confidence_pct = 0.0

    raw_probs = data.get("probabilities") or {}
    probability_rows = []
    for label in TRIAGE_RISK_LABELS:
        try:
            value = float(raw_probs.get(label, 0.0))
        except (TypeError, ValueError):
            value = 0.0
        value = max(0.0, min(1.0, value))
        probability_rows.append(
            {
                "label": label,
                "display": TRIAGE_RISK_DISPLAY.get(label, label.capitalize()),
                "tone": label,
                "value": value,
                "percent": round(value * 100, 2),
            }
        )

    contributors = []
    for item in data.get("top_contributors") or []:
        if not isinstance(item, dict):
            continue
        contributors.append(
            {
                "feature": str(item.get("feature", "")),
                "importance": item.get("importance"),
                "value": item.get("value"),
            }
        )

    alerts = [str(a) for a in (data.get("alerts") or []) if a]

    return {
        "risk_level": risk,
        "risk_display": TRIAGE_RISK_DISPLAY.get(risk, risk.capitalize() or "Sin clase"),
        "priority": priority,
        "priority_display": TRIAGE_PRIORITY_DISPLAY.get(priority, priority.capitalize() or "-"),
        "confidence": confidence_pct,
        "probability_rows": probability_rows,
        "top_contributors": contributors,
        "alerts": alerts,
        "model_name": data.get("model_name"),
        "model_version": data.get("model_version"),
        "model_family": data.get("model_family"),
        "score": data.get("score"),
        "triage_id": data.get("triage_id"),
        "clinical_note": data.get("clinical_note"),
    }
