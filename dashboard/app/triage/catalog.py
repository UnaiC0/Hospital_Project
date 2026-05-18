from __future__ import annotations

TRIAGE_SYMPTOMS = [
    ("chest pain", "Dolor toracico"),
    ("shortness of breath", "Disnea"),
    ("loss of consciousness", "Perdida de conciencia"),
    ("fever", "Fiebre"),
    ("cough", "Tos"),
    ("abdominal pain", "Dolor abdominal"),
    ("headache", "Cefalea"),
    ("dizziness", "Mareo"),
    ("vomiting", "Vomitos"),
    ("bleeding", "Sangrado"),
]

TRIAGE_VITAL_FIELDS = [
    ("age", "Edad", 45, "anos", 0, 120),
    ("heart_rate", "Frecuencia cardiaca", 80, "lpm", 20, 220),
    ("oxygen_saturation", "Saturacion O2", 98, "%", 50, 100),
    ("systolic_bp", "Presion sistolica", 120, "mmHg", 40, 260),
    ("respiratory_rate", "Frec. respiratoria", 16, "rpm", 4, 60),
    ("temperature", "Temperatura", 36.8, "C", 30, 43),
]

TRIAGE_RISK_LABELS = ["low", "medium", "high", "critical"]

TRIAGE_RISK_DISPLAY = {
    "low": "Bajo",
    "medium": "Medio",
    "high": "Alto",
    "critical": "Critico",
}

TRIAGE_PRIORITY_DISPLAY = {
    "standard": "Estandar",
    "priority": "Prioritario",
    "urgent": "Urgente",
    "immediate": "Inmediato",
}
