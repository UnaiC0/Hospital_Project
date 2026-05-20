from __future__ import annotations

from typing import Any

from app.triage.catalog import TRIAGE_SYMPTOMS, TRIAGE_VITAL_FIELDS


class TriageValidationError(ValueError):
    pass


def parse_triage_form(form: Any) -> tuple[dict, dict]:
    patient_name = (form.get("patient_name") or "").strip()
    if not patient_name:
        raise TriageValidationError("El nombre del paciente es obligatorio.")

    vitals: dict[str, float] = {}
    raw_values: dict[str, Any] = {"patient_name": patient_name}
    for key, _label, default, _unit, vmin, vmax in TRIAGE_VITAL_FIELDS:
        raw = (form.get(key) or "").strip()
        raw_values[key] = raw
        if raw == "":
            vitals[key] = float(default)
            continue
        try:
            value = float(raw.replace(",", "."))
        except ValueError as exc:
            raise TriageValidationError(f"El campo '{key}' debe ser numerico.") from exc
        if value < vmin or value > vmax:
            raise TriageValidationError(
                f"El campo '{key}' debe estar entre {vmin} y {vmax}."
            )
        vitals[key] = value

    selected = form.getlist("symptoms") if hasattr(form, "getlist") else []
    valid_symptoms = {s for s, _ in TRIAGE_SYMPTOMS}
    symptoms = [s for s in selected if s in valid_symptoms]

    payload = {"patient_name": patient_name, "symptoms": symptoms, "vitals": vitals}
    raw_values["symptoms"] = symptoms
    return payload, raw_values


def empty_triage_form_values() -> dict:
    values: dict[str, Any] = {key: "" for key, *_ in TRIAGE_VITAL_FIELDS}
    values["patient_name"] = ""
    values["symptoms"] = []
    return values
