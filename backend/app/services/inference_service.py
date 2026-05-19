from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any

import torch
from PIL import Image, ImageStat
from torch import nn
from torchvision import models, transforms


CLINICAL_EXPLANATIONS = {
    "Sana": "La distribucion de intensidad se aproxima al patron basal definido para estudios sin hallazgos dominantes.",
    "Neumonia": "La imagen concentra rasgos de intensidad y contraste compatibles con infiltrados, por lo que debe revisarse clinicamente.",
    "COVID-19": "La lectura muestra un patron que el sistema marca para descarte de COVID-19 y seguimiento epidemiologico.",
}

CLINICAL_NOTE = (
    "Resultado de apoyo: no sustituye la valoracion del personal sanitario ni "
    "debe utilizarse como diagnostico autonomo."
)

DEFAULT_MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models"))
DEFAULT_MODEL_FILE = os.getenv("RADIOLOGY_MODEL_FILE", "radiology_cnn_resnet18.pt")


class InferenceService:
    """ResNet18 inference for chest radiographs.

    Loads the checkpoint produced by ml/train_cnn.py once and reuses it for every
    request. The checkpoint carries its own class_names and preprocessing contract
    so the service stays consistent with whatever the trainer produced.
    """

    model_family = "resnet18"

    def __init__(
        self,
        model: nn.Module,
        class_names: list[str],
        preprocessing: dict[str, Any],
        model_name: str,
        model_version: str,
        device: torch.device,
    ):
        self._model = model
        self._class_names = class_names
        self._preprocessing = preprocessing
        self._device = device
        self.model_name = model_name
        self.model_version = model_version
        self._transform = _build_transform(preprocessing)

    def predict(self, image_bytes: bytes) -> dict[str, Any]:
        probabilities = self._infer(image_bytes)
        predicted_class = max(probabilities, key=probabilities.get)
        confidence = probabilities[predicted_class]
        mean_intensity, contrast = self._compute_features(image_bytes)
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
            "preprocessing": self._preprocessing,
            "quality_flags": quality_flags,
            "explanation": CLINICAL_EXPLANATIONS.get(predicted_class, ""),
            "clinical_note": CLINICAL_NOTE,
        }

    def _infer(self, image_bytes: bytes) -> dict[str, float]:
        with Image.open(BytesIO(image_bytes)) as image:
            rgb = image.convert("RGB")
            tensor = self._transform(rgb).unsqueeze(0).to(self._device)
        with torch.no_grad():
            logits = self._model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        return {
            label: round(float(prob), 4)
            for label, prob in zip(self._class_names, probs)
        }

    @staticmethod
    def _compute_features(image_bytes: bytes) -> tuple[float, float]:
        with Image.open(BytesIO(image_bytes)) as image:
            grayscale = image.convert("L").resize((256, 256))
            stats = ImageStat.Stat(grayscale)
        return float(stats.mean[0]), float(stats.stddev[0])

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


def _build_transform(preprocessing: dict[str, Any]):
    size = preprocessing.get("input", {}).get("size") or preprocessing.get("size") or [224, 224]
    mean = (
        preprocessing.get("input", {}).get("normalization_mean")
        or preprocessing.get("normalization_mean")
        or [0.485, 0.456, 0.406]
    )
    std = (
        preprocessing.get("input", {}).get("normalization_std")
        or preprocessing.get("normalization_std")
        or [0.229, 0.224, 0.225]
    )
    return transforms.Compose(
        [
            transforms.Resize((int(size[0]), int(size[1]))),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )


def build_inference_service() -> InferenceService:
    model_path = DEFAULT_MODEL_DIR / DEFAULT_MODEL_FILE
    if not model_path.exists():
        raise FileNotFoundError(
            f"Checkpoint no encontrado en {model_path}. "
            "Entrena el modelo (profile training) o ajusta MODEL_DIR/RADIOLOGY_MODEL_FILE."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)

    class_names = list(checkpoint["class_names"])
    state_dict = checkpoint["state_dict"]
    preprocessing = checkpoint.get("preprocessing", {})
    model_name = str(checkpoint.get("model_name", "radiology-cnn-resnet18"))
    model_version = str(checkpoint.get("model_version", "0.0.0"))

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    return InferenceService(
        model=model,
        class_names=class_names,
        preprocessing=preprocessing,
        model_name=model_name,
        model_version=model_version,
        device=device,
    )
