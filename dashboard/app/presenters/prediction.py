from __future__ import annotations

import base64
from typing import Any


DISPLAY_ORDER = ["Sana", "Neumonia", "COVID-19"]
PROBABILITY_TONES = {"Sana": "healthy", "Neumonia": "pneumonia", "COVID-19": "covid"}
RESULT_CONTENT: dict[str, dict[str, str]] = {
    "Sana": {
        "slug": "healthy",
        "title": "Sana",
        "icon": "verified",
        "description": (
            "No se observan hallazgos dominantes compatibles con neumonia o COVID-19. "
            "La revision medica debe confirmar la interpretacion clinica final."
        ),
    },
    "Neumonia": {
        "slug": "pneumonia",
        "title": "Neumonia",
        "icon": "warning",
        "description": (
            "Se observan patrones compatibles con infiltrados pulmonares. "
            "Se recomienda correlacion clinica inmediata por parte del especialista."
        ),
    },
    "COVID-19": {
        "slug": "covid",
        "title": "COVID-19",
        "icon": "coronavirus",
        "description": (
            "La imagen presenta rasgos que requieren descarte clinico dirigido de COVID-19. "
            "La valoracion definitiva debe integrarse con sintomas y pruebas complementarias."
        ),
    },
}


def build_image_preview(file_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def format_file_size(file_bytes: bytes) -> str:
    return f"{len(file_bytes) / (1024 * 1024):.1f} MB"


def normalize_probabilities(probabilities: list[tuple[str, float]] | None) -> list[dict[str, Any]]:
    lookup: dict[str, float] = {}
    if probabilities:
        lookup = {str(label): max(0.0, min(1.0, float(value))) for label, value in probabilities}
    rows: list[dict[str, Any]] = []
    for label in DISPLAY_ORDER:
        value = lookup.get(label, 0.0)
        rows.append({
            "label": label,
            "value": value,
            "percent": round(value * 100, 2),
            "tone": PROBABILITY_TONES[label],
        })
    return rows


def build_result_context(prediction_class: str | None) -> dict[str, str]:
    if prediction_class in RESULT_CONTENT:
        result = RESULT_CONTENT[prediction_class]
        return {
            "state": result["slug"],
            "title": result["title"],
            "icon": result["icon"],
            "description": result["description"],
            "eyebrow": "Resultado detectado",
        }
    return {
        "state": "pending",
        "title": "Esperando analisis",
        "icon": "pending",
        "description": (
            "Cargue una radiografia valida para generar la clasificacion asistida y "
            "las probabilidades del estudio."
        ),
        "eyebrow": "Estado del diagnostico",
    }


def normalize_backend_prediction(payload: dict[str, Any]) -> dict[str, Any]:
    """Adapts the backend /predict response to the format the view expects."""
    prediction_class = payload.get("class")
    probabilities = payload.get("probabilities")
    if not isinstance(prediction_class, str) or not isinstance(probabilities, dict):
        raise ValueError("La respuesta del backend no tiene el formato esperado.")

    normalized: list[tuple[str, float]] = []
    for label, value in probabilities.items():
        try:
            normalized.append((str(label), float(value)))
        except (TypeError, ValueError) as exc:
            raise ValueError("La respuesta del backend no tiene el formato esperado.") from exc
    normalized.sort(key=lambda item: item[1], reverse=True)

    storage = payload.get("storage") if isinstance(payload.get("storage"), dict) else {}
    quality_flags = payload.get("quality_flags") if isinstance(payload.get("quality_flags"), list) else []
    events = payload.get("events") if isinstance(payload.get("events"), list) else []
    return {
        "class": prediction_class,
        "probabilities": normalized,
        "study_id": payload.get("study_id"),
        "created_at": payload.get("created_at"),
        "confidence": payload.get("confidence"),
        "storage": storage,
        "quality_status": payload.get("quality_status"),
        "quality_flags": quality_flags,
        "events": events,
    }
