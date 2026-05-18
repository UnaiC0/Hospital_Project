from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image, ImageStat


CLINICAL_EXPLANATIONS = {
    "Sana": "La distribucion de intensidad se aproxima al patron basal definido para estudios sin hallazgos dominantes.",
    "Neumonia": "La imagen concentra rasgos de intensidad y contraste compatibles con infiltrados, por lo que debe revisarse clinicamente.",
    "COVID-19": "La lectura muestra un patron que el sistema marca para descarte de COVID-19 y seguimiento epidemiologico.",
}

CLINICAL_NOTE = (
    "Resultado de apoyo: no sustituye la valoracion del personal sanitario ni "
    "debe utilizarse como diagnostico autonomo."
)


class InferenceService:
    """Baseline inference engine based on grayscale intensity statistics.

    This is a placeholder for the CNN model. The contract is the only thing other
    layers depend on, so swapping in a trained model is a single-file change.
    """

    model_name = "radiology-baseline-image-statistics"
    model_version = "0.2.0"
    model_family = "baseline_pre_deep_learning"

    def predict(self, image_bytes: bytes) -> dict[str, Any]:
        mean_intensity, contrast = self._compute_features(image_bytes)
        probabilities = self._compute_probabilities(mean_intensity, contrast)
        predicted_class = max(probabilities, key=probabilities.get)
        confidence = probabilities[predicted_class]
        quality_flags = self._compute_quality_flags(mean_intensity, contrast, confidence)

        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_family": self.model_family,
            "class": predicted_class,
            "probabilities": probabilities,
            "confidence": confidence,
            "features": {
                "mean_intensity": round(mean_intensity, 2),
                "contrast": round(contrast, 2),
                "input_size_bytes": len(image_bytes),
            },
            "preprocessing": {
                "color_space": "grayscale",
                "resize": [256, 256],
                "normalization": "statistical_baseline",
            },
            "quality_flags": quality_flags,
            "explanation": CLINICAL_EXPLANATIONS[predicted_class],
            "clinical_note": CLINICAL_NOTE,
        }

    @staticmethod
    def _compute_features(image_bytes: bytes) -> tuple[float, float]:
        with Image.open(BytesIO(image_bytes)) as image:
            grayscale = image.convert("L").resize((256, 256))
            stats = ImageStat.Stat(grayscale)
        return float(stats.mean[0]), float(stats.stddev[0])

    @staticmethod
    def _compute_probabilities(mean_intensity: float, contrast: float) -> dict[str, float]:
        raw_scores = {
            "Sana": max(
                0.05,
                1.45 - abs(mean_intensity - 185.0) / 115.0 - abs(contrast - 42.0) / 65.0,
            ),
            "Neumonia": max(
                0.05,
                1.20 - abs(mean_intensity - 125.0) / 95.0 + contrast / 135.0,
            ),
            "COVID-19": max(
                0.05,
                1.15 - abs(mean_intensity - 95.0) / 90.0 + max(0.0, 55.0 - contrast) / 90.0,
            ),
        }
        total = sum(raw_scores.values())
        return {label: round(score / total, 4) for label, score in raw_scores.items()}

    @staticmethod
    def _compute_quality_flags(mean_intensity: float, contrast: float, confidence: float) -> list[str]:
        flags: list[str] = []
        if mean_intensity < 45:
            flags.append("Imagen muy oscura: revisar exposicion o contraste antes de decidir.")
        if mean_intensity > 230:
            flags.append("Imagen muy clara: puede perder detalles pulmonares relevantes.")
        if contrast < 18:
            flags.append("Contraste bajo: el estudio puede ser dificil de interpretar.")
        if confidence < 0.55:
            flags.append("Prediccion con baja confianza: requiere revision medica prioritaria.")
        return flags


def build_inference_service() -> InferenceService:
    return InferenceService()
