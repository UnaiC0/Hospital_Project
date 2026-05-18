from __future__ import annotations

from typing import Any

import requests

from app.core.config import BackendSettings


class BackendError(RuntimeError):
    pass


class BackendClient:
    """Typed adapter to the backend FastAPI service. Hides HTTP transport so
    blueprints depend on an interface, not the requests library."""

    def __init__(self, settings: BackendSettings, timeout_seconds: float = 30.0):
        self._base_url = settings.base_url
        self._timeout = timeout_seconds

    # ---- write paths ----
    def request_prediction(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        source_object_key: str | None = None,
    ) -> dict[str, Any]:
        data = {}
        if source_object_key:
            data["source_object_key"] = source_object_key
        try:
            response = requests.post(
                f"{self._base_url}/predict",
                files={"file": (filename, file_bytes, mime_type)},
                data=data,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise BackendError("No se pudo conectar con el backend de prediccion.") from exc

        payload = self._parse_json(response)
        if response.status_code != 200:
            detail = payload.get("detail") if isinstance(payload, dict) else None
            raise BackendError(detail if isinstance(detail, str) and detail else "No se pudo obtener la prediccion.")
        if not isinstance(payload, dict):
            raise BackendError("La respuesta del backend no es valida.")
        return payload

    def request_triage(self, payload: dict) -> dict[str, Any]:
        try:
            response = requests.post(
                f"{self._base_url}/triage",
                json=payload,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise BackendError("No se pudo conectar con el backend de triaje.") from exc

        data = self._parse_json(response)
        if response.status_code != 200:
            detail = data.get("detail") if isinstance(data, dict) else None
            raise BackendError(detail if isinstance(detail, str) and detail else "El backend no pudo evaluar el triaje.")
        if not isinstance(data, dict):
            raise BackendError("La respuesta del backend no tiene el formato esperado.")
        return data

    # ---- read paths ----
    def get(self, path: str, default: Any) -> Any:
        try:
            response = requests.get(f"{self._base_url}{path}", timeout=5)
            if response.status_code != 200:
                return default
            return response.json()
        except requests.RequestException:
            return default

    @staticmethod
    def _parse_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise BackendError("La respuesta del backend no es valida.") from exc
