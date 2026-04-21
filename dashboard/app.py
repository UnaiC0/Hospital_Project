import base64
import os
from io import BytesIO
from uuid import uuid4

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_FORMATS = {
    "JPEG": {"extensions": {"jpg", "jpeg"}, "mime_type": "image/jpeg"},
    "PNG": {"extensions": {"png"}, "mime_type": "image/png"},
}
DISPLAY_ORDER = ["Sana", "Neumonia", "COVID-19"]
PROBABILITY_TONES = {
    "Sana": "healthy",
    "Neumonia": "pneumonia",
    "COVID-19": "covid",
}
RESULT_CONTENT = {
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
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000").rstrip("/")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000").rstrip("/")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "hospital-data")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")
MINIO_CONSOLE_URL = os.getenv("MINIO_CONSOLE_URL", "http://localhost:9001").rstrip("/")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


class ValidationError(Exception):
    pass


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name=MINIO_REGION,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def ensure_minio_bucket(client) -> None:
    try:
        client.head_bucket(Bucket=MINIO_BUCKET_NAME)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise
        client.create_bucket(Bucket=MINIO_BUCKET_NAME)


def object_exists(client, object_key: str) -> bool:
    try:
        client.head_object(Bucket=MINIO_BUCKET_NAME, Key=object_key)
        return True
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


def generate_object_key(client, extension: str) -> str:
    for _ in range(10):
        object_key = f"uploads/{uuid4().hex}.{extension}"
        if not object_exists(client, object_key):
            return object_key
    raise RuntimeError("No se pudo generar un nombre unico para la imagen.")


def validate_uploaded_file(file_storage) -> dict[str, str | bytes]:
    if file_storage is None:
        raise ValidationError("Debe seleccionar una imagen.")

    original_name = secure_filename(file_storage.filename or "")
    if not original_name:
        raise ValidationError("El nombre del archivo no es valido.")

    if "." not in original_name:
        raise ValidationError("El archivo debe tener extension.")

    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Formato no permitido. Use JPG, JPEG o PNG.")

    file_bytes = file_storage.read()
    if not file_bytes:
        raise ValidationError("El archivo esta vacio.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValidationError("El archivo supera el tamano maximo de 5 MB.")

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()
        with Image.open(BytesIO(file_bytes)) as image:
            detected_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("El archivo no es una imagen valida.") from exc

    format_config = ALLOWED_FORMATS.get(detected_format)
    if not format_config:
        raise ValidationError("Formato no permitido. Use JPG, JPEG o PNG.")

    if extension not in format_config["extensions"]:
        raise ValidationError("La extension no coincide con el contenido de la imagen.")

    return {
        "original_name": original_name,
        "extension": extension,
        "mime_type": format_config["mime_type"],
        "file_bytes": file_bytes,
    }


def build_image_preview(file_bytes: bytes, mime_type: str) -> str:
    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"


def upload_to_minio(file_bytes: bytes, extension: str, mime_type: str) -> str:
    try:
        client = get_minio_client()
        ensure_minio_bucket(client)
        object_key = generate_object_key(client, extension)
        client.put_object(
            Bucket=MINIO_BUCKET_NAME,
            Key=object_key,
            Body=file_bytes,
            ContentType=mime_type,
        )
        return object_key
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError("No se pudo subir la imagen a MinIO.") from exc


def request_prediction(file_bytes: bytes, filename: str, mime_type: str) -> dict[str, object]:
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            files={"file": (filename, file_bytes, mime_type)},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise RuntimeError("No se pudo conectar con el backend de prediccion.") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("La respuesta del backend no es valida.") from exc

    if response.status_code != 200:
        detail = payload.get("detail") if isinstance(payload, dict) else None
        if isinstance(detail, str) and detail:
            raise RuntimeError(detail)
        raise RuntimeError("No se pudo obtener la prediccion.")

    if not isinstance(payload, dict):
        raise RuntimeError("La respuesta del backend no es valida.")

    prediction_class = payload.get("class")
    probabilities = payload.get("probabilities")
    if not isinstance(prediction_class, str) or not isinstance(probabilities, dict):
        raise RuntimeError("La respuesta del backend no tiene el formato esperado.")

    normalized_probabilities = []
    for label, value in probabilities.items():
        try:
            normalized_probabilities.append((str(label), float(value)))
        except (TypeError, ValueError) as exc:
            raise RuntimeError("La respuesta del backend no tiene el formato esperado.") from exc

    normalized_probabilities.sort(key=lambda item: item[1], reverse=True)

    return {
        "class": prediction_class,
        "probabilities": normalized_probabilities,
    }


def format_file_size(file_bytes: bytes) -> str:
    return f"{len(file_bytes) / (1024 * 1024):.1f} MB"


def normalize_probabilities(probabilities=None):
    probability_lookup = {}
    if probabilities:
        probability_lookup = {
            str(label): max(0.0, min(1.0, float(value)))
            for label, value in probabilities
        }

    rows = []
    for label in DISPLAY_ORDER:
        value = probability_lookup.get(label, 0.0)
        rows.append(
            {
                "label": label,
                "value": value,
                "percent": round(value * 100, 2),
                "tone": PROBABILITY_TONES[label],
            }
        )
    return rows


def build_result_context(prediction_class=None):
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


def build_template_context(
    *,
    error=None,
    success=None,
    image_preview=None,
    prediction_class=None,
    probabilities=None,
    object_key=None,
    uploaded_filename=None,
    uploaded_size=None,
):
    has_image = bool(image_preview)
    has_result = bool(prediction_class)
    result = build_result_context(prediction_class)

    if uploaded_filename and uploaded_size and has_result:
        file_status = f"{uploaded_size} - Analisis completado"
    elif uploaded_filename and uploaded_size:
        file_status = f"{uploaded_size} - Listo para procesar"
    else:
        file_status = "Seleccione una radiografia JPG, JPEG o PNG"

    return {
        "error": error,
        "success": success,
        "image_preview": image_preview,
        "prediction_class": prediction_class,
        "probability_rows": normalize_probabilities(probabilities),
        "object_key": object_key,
        "uploaded_filename": uploaded_filename or "Ningun archivo cargado",
        "uploaded_size": uploaded_size,
        "file_status": file_status,
        "has_image": has_image,
        "has_result": has_result,
        "result": result,
        "minio_bucket_name": MINIO_BUCKET_NAME,
        "minio_console_url": MINIO_CONSOLE_URL,
        "minio_endpoint": MINIO_ENDPOINT,
    }


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(_error):
    return (
        render_template(
            "index.html",
            **build_template_context(
                error="El archivo supera el tamano maximo de 5 MB.",
            ),
        ),
        413,
    )


@app.get("/")
def index():
    return render_template("index.html", **build_template_context())


@app.post("/upload")
def upload():
    image_preview = None
    uploaded_filename = None
    uploaded_size = None

    try:
        uploaded_file = request.files.get("file")
        validated_file = validate_uploaded_file(uploaded_file)
        uploaded_filename = validated_file["original_name"]
        uploaded_size = format_file_size(validated_file["file_bytes"])
        image_preview = build_image_preview(
            validated_file["file_bytes"],
            validated_file["mime_type"],
        )
        object_key = upload_to_minio(
            validated_file["file_bytes"],
            validated_file["extension"],
            validated_file["mime_type"],
        )
        prediction = request_prediction(
            validated_file["file_bytes"],
            validated_file["original_name"],
            validated_file["mime_type"],
        )

        return render_template(
            "index.html",
            **build_template_context(
                success="Imagen procesada correctamente.",
                image_preview=image_preview,
                prediction_class=prediction["class"],
                probabilities=prediction["probabilities"],
                object_key=object_key,
                uploaded_filename=uploaded_filename,
                uploaded_size=uploaded_size,
            ),
        )
    except ValidationError as exc:
        return (
            render_template(
                "index.html",
                **build_template_context(
                    error=str(exc),
                    image_preview=image_preview,
                    uploaded_filename=uploaded_filename,
                    uploaded_size=uploaded_size,
                ),
            ),
            400,
        )
    except RuntimeError as exc:
        return (
            render_template(
                "index.html",
                **build_template_context(
                    error=str(exc),
                    image_preview=image_preview,
                    uploaded_filename=uploaded_filename,
                    uploaded_size=uploaded_size,
                ),
            ),
            502,
        )
    except Exception:
        return (
            render_template(
                "index.html",
                **build_template_context(
                    error="Se produjo un error interno al procesar la solicitud.",
                    image_preview=image_preview,
                    uploaded_filename=uploaded_filename,
                    uploaded_size=uploaded_size,
                ),
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=False)
