import json
import os
import hashlib
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from uuid import uuid4

import boto3
import psycopg
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, ImageStat, UnidentifiedImageError
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from app import triage_model


def required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = required_env("POSTGRES_USER")
POSTGRES_PASSWORD = required_env("POSTGRES_PASSWORD")
POSTGRES_DB = required_env("POSTGRES_DB")
MINIO_ENDPOINT = required_env("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = required_env("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = required_env("MINIO_SECRET_KEY")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")
MINIO_BUCKET_NAME = required_env("MINIO_BUCKET_NAME")
MINIO_AUTO_CREATE_BUCKET = os.getenv("MINIO_AUTO_CREATE_BUCKET", "false").lower() == "true"
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://spark:7077")
ALLOWED_PREDICT_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_PREDICT_MIME_TYPES = {"image/jpeg", "image/png"}
PREDICT_FORMAT_EXTENSIONS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
}
MAX_PREDICT_FILE_SIZE = 5 * 1024 * 1024


def get_db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        connect_timeout=5,
        row_factory=dict_row,
    )


def get_minio_client():
    client_kwargs: dict[str, Any] = {
        "service_name": "s3",
        "region_name": MINIO_REGION,
        "config": Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    }
    if MINIO_ENDPOINT:
        client_kwargs["endpoint_url"] = MINIO_ENDPOINT
    if MINIO_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = MINIO_ACCESS_KEY
    if MINIO_SECRET_KEY:
        client_kwargs["aws_secret_access_key"] = MINIO_SECRET_KEY

    return boto3.client(**client_kwargs)


def ensure_database_schema() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS triage_records (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL,
        request_payload JSONB NOT NULL,
        model_response JSONB NOT NULL,
        risk_level TEXT NOT NULL,
        recommended_priority TEXT NOT NULL,
        score INTEGER NOT NULL,
        confidence DOUBLE PRECISION NOT NULL,
        report_bucket TEXT NOT NULL,
        report_object_key TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS triage_records_created_at_idx
    ON triage_records (created_at DESC);

    CREATE TABLE IF NOT EXISTS radiology_studies (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL,
        original_filename TEXT NOT NULL,
        content_type TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        checksum_sha256 TEXT NOT NULL,
        image_bucket TEXT,
        image_object_key TEXT,
        prediction_class TEXT NOT NULL,
        probabilities JSONB NOT NULL,
        model_name TEXT NOT NULL,
        model_version TEXT NOT NULL,
        confidence DOUBLE PRECISION NOT NULL,
        quality_status TEXT NOT NULL,
        quality_messages JSONB NOT NULL,
        model_response JSONB NOT NULL,
        report_bucket TEXT NOT NULL,
        report_object_key TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS radiology_studies_created_at_idx
    ON radiology_studies (created_at DESC);

    CREATE INDEX IF NOT EXISTS radiology_studies_prediction_class_idx
    ON radiology_studies (prediction_class);

    CREATE TABLE IF NOT EXISTS quality_events (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL,
        source TEXT NOT NULL,
        severity TEXT NOT NULL,
        event_type TEXT NOT NULL,
        message TEXT NOT NULL,
        metadata JSONB NOT NULL,
        resolved BOOLEAN NOT NULL DEFAULT FALSE
    );

    CREATE INDEX IF NOT EXISTS quality_events_created_at_idx
    ON quality_events (created_at DESC);

    CREATE TABLE IF NOT EXISTS pipeline_runs (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL,
        finished_at TIMESTAMPTZ,
        status TEXT NOT NULL,
        input_uri TEXT NOT NULL,
        processed_count INTEGER NOT NULL DEFAULT 0,
        rejected_count INTEGER NOT NULL DEFAULT 0,
        report_bucket TEXT,
        report_object_key TEXT,
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb
    );

    CREATE INDEX IF NOT EXISTS pipeline_runs_created_at_idx
    ON pipeline_runs (created_at DESC);
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()


def create_minio_bucket(client) -> None:
    if MINIO_REGION == "us-east-1":
        client.create_bucket(Bucket=MINIO_BUCKET_NAME)
        return

    client.create_bucket(
        Bucket=MINIO_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": MINIO_REGION},
    )


def validate_minio_bucket() -> None:
    if not MINIO_BUCKET_NAME:
        raise RuntimeError("MINIO_BUCKET_NAME is not configured")

    client = get_minio_client()
    try:
        client.head_bucket(Bucket=MINIO_BUCKET_NAME)
    except NoCredentialsError as exc:
        raise RuntimeError("MinIO credentials are not configured") from exc
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"404", "NoSuchBucket"} and MINIO_AUTO_CREATE_BUCKET:
            create_minio_bucket(client)
            return
        raise RuntimeError(
            f"MinIO bucket '{MINIO_BUCKET_NAME}' is not accessible: {error_code or exc}"
        ) from exc


def retry_operation(operation, label: str, attempts: int = 10, delay_seconds: float = 2.0) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            operation()
            return
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(delay_seconds)
    raise RuntimeError(f"{label} initialization failed") from last_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    retry_operation(ensure_database_schema, "PostgreSQL schema")
    yield


app = FastAPI(title="Hospital Backend", version="2.0.0", lifespan=lifespan)


class TriageRequest(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    vitals: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


def compute_triage_baseline(payload: TriageRequest) -> dict[str, Any]:
    symptoms = {symptom.strip().lower() for symptom in payload.symptoms if symptom}
    heart_rate = float(payload.vitals.get("heart_rate", 0) or 0)
    oxygen_saturation = float(payload.vitals.get("oxygen_saturation", 100) or 100)
    systolic_bp = float(payload.vitals.get("systolic_bp", 120) or 120)

    score = min(len(symptoms) * 8, 40)

    if {"chest pain", "shortness of breath", "loss of consciousness"} & symptoms:
        score += 35
    if heart_rate >= 120:
        score += 15
    if oxygen_saturation < 92:
        score += 25
    if systolic_bp < 90:
        score += 20

    score = min(score, 100)

    if score >= 75:
        risk_level = "critical"
        recommended_priority = "immediate"
    elif score >= 50:
        risk_level = "high"
        recommended_priority = "urgent"
    elif score >= 25:
        risk_level = "medium"
        recommended_priority = "priority"
    else:
        risk_level = "low"
        recommended_priority = "standard"

    return {
        "model_name": "hospital-triage-rules-fallback",
        "model_version": "0.0.1",
        "model_family": "rule_based_baseline",
        "risk_level": risk_level,
        "recommended_priority": recommended_priority,
        "confidence": round(0.65 + (score / 200), 2),
        "score": score,
        "probabilities": {},
        "top_contributors": [],
        "alerts": [],
        "clinical_note": (
            "Resultado generado por reglas baseline porque no hay modelo "
            "entrenado disponible. Apoyo a la decision, no diagnostico."
        ),
    }


def compute_triage(payload: TriageRequest) -> dict[str, Any]:
    model_result = triage_model.predict(payload.symptoms, payload.vitals)
    if model_result is not None:
        return model_result
    return compute_triage_baseline(payload)


async def read_and_validate_prediction_file(upload_file: UploadFile) -> bytes:
    filename = (upload_file.filename or "").strip()
    if not filename:
        raise ValueError("A file is required")

    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_PREDICT_EXTENSIONS:
        raise ValueError("Unsupported file type")

    content_type = (upload_file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_PREDICT_MIME_TYPES:
        raise ValueError("Unsupported file type")

    image_bytes = await upload_file.read()
    if not image_bytes:
        raise ValueError("Empty file")

    if len(image_bytes) > MAX_PREDICT_FILE_SIZE:
        raise ValueError("File exceeds the 5MB limit")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
        with Image.open(BytesIO(image_bytes)) as image:
            detected_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Invalid image file") from exc

    allowed_extensions = PREDICT_FORMAT_EXTENSIONS.get(detected_format)
    if not allowed_extensions:
        raise ValueError("Unsupported image format")

    if extension not in allowed_extensions:
        raise ValueError("File extension does not match the image content")

    return image_bytes


def infer_xray_prediction(image_bytes: bytes) -> dict[str, Any]:
    with Image.open(BytesIO(image_bytes)) as image:
        grayscale_image = image.convert("L").resize((256, 256))
        stats = ImageStat.Stat(grayscale_image)

    mean_intensity = float(stats.mean[0])
    contrast = float(stats.stddev[0])

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

    total_score = sum(raw_scores.values())
    probabilities = {
        label: round(score / total_score, 4)
        for label, score in raw_scores.items()
    }
    predicted_class = max(probabilities, key=probabilities.get)
    confidence = probabilities[predicted_class]

    quality_flags: list[str] = []
    if mean_intensity < 45:
        quality_flags.append("Imagen muy oscura: revisar exposicion o contraste antes de decidir.")
    if mean_intensity > 230:
        quality_flags.append("Imagen muy clara: puede perder detalles pulmonares relevantes.")
    if contrast < 18:
        quality_flags.append("Contraste bajo: el estudio puede ser dificil de interpretar.")
    if confidence < 0.55:
        quality_flags.append("Prediccion con baja confianza: requiere revision medica prioritaria.")

    explanation_lookup = {
        "Sana": "La distribucion de intensidad se aproxima al patron basal definido para estudios sin hallazgos dominantes.",
        "Neumonia": "La imagen concentra rasgos de intensidad y contraste compatibles con infiltrados, por lo que debe revisarse clinicamente.",
        "COVID-19": "La lectura muestra un patron que el sistema marca para descarte de COVID-19 y seguimiento epidemiologico.",
    }

    return {
        "model_name": "radiology-baseline-image-statistics",
        "model_version": "0.2.0",
        "model_family": "baseline_pre_deep_learning",
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
        "explanation": explanation_lookup[predicted_class],
        "clinical_note": (
            "Resultado de apoyo: no sustituye la valoracion del personal sanitario ni "
            "debe utilizarse como diagnostico autonomo."
        ),
    }


def get_postgres_status() -> str:
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


def get_minio_status() -> str:
    try:
        validate_minio_bucket()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


def record_quality_event(
    *,
    source: str,
    severity: str,
    event_type: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    insert_query = """
    INSERT INTO quality_events (
        id,
        created_at,
        source,
        severity,
        event_type,
        message,
        metadata
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb);
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                insert_query,
                (
                    event_id,
                    created_at,
                    source,
                    severity,
                    event_type,
                    message,
                    json.dumps(metadata or {}),
                ),
            )
        connection.commit()

    return {
        "event_id": event_id,
        "created_at": created_at.isoformat(),
        "source": source,
        "severity": severity,
        "event_type": event_type,
        "message": message,
        "metadata": metadata or {},
    }


def persist_radiology_study(
    *,
    original_filename: str,
    content_type: str,
    image_bytes: bytes,
    prediction: dict[str, Any],
    source_object_key: str | None,
) -> dict[str, Any]:
    study_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    checksum_sha256 = hashlib.sha256(image_bytes).hexdigest()
    report_object_key = f"radiology-reports/{study_id}.json"
    quality_messages = prediction.get("quality_flags", [])
    if not isinstance(quality_messages, list):
        quality_messages = []
    quality_status = "warning" if quality_messages else "accepted"
    probabilities = prediction.get("probabilities", {})
    prediction_class = str(prediction.get("class", "unknown"))
    confidence = float(prediction.get("confidence", 0.0) or 0.0)
    model_name = str(prediction.get("model_name", "unknown"))
    model_version = str(prediction.get("model_version", "unknown"))
    stored_image_object_key = source_object_key

    minio_client = get_minio_client()
    validate_minio_bucket()
    if not stored_image_object_key:
        extension = os.path.splitext(original_filename)[1].lower() or ".jpg"
        stored_image_object_key = f"uploads/{study_id}{extension}"
        minio_client.put_object(
            Bucket=MINIO_BUCKET_NAME,
            Key=stored_image_object_key,
            Body=image_bytes,
            ContentType=content_type,
        )

    report_document = {
        "study_id": study_id,
        "created_at": created_at.isoformat(),
        "image": {
            "original_filename": original_filename,
            "content_type": content_type,
            "file_size_bytes": len(image_bytes),
            "checksum_sha256": checksum_sha256,
            "bucket": MINIO_BUCKET_NAME,
            "object_key": stored_image_object_key,
        },
        "prediction": prediction,
        "quality": {
            "status": quality_status,
            "messages": quality_messages,
        },
        "automation": {
            "report_object_key": report_object_key,
            "alerts": [],
        },
    }

    if prediction_class == "COVID-19":
        report_document["automation"]["alerts"].append(
            "Priorizar revision medica y activar protocolo de enfermedad contagiosa."
        )
    if confidence < 0.55:
        report_document["automation"]["alerts"].append(
            "Enviar a cola de revision por baja confianza del modelo."
        )
    if quality_messages:
        report_document["automation"]["alerts"].append(
            "Repetir o validar estudio por posibles problemas de calidad."
        )

    minio_client.put_object(
        Bucket=MINIO_BUCKET_NAME,
        Key=report_object_key,
        Body=json.dumps(report_document).encode("utf-8"),
        ContentType="application/json",
    )

    insert_query = """
    INSERT INTO radiology_studies (
        id,
        created_at,
        original_filename,
        content_type,
        file_size_bytes,
        checksum_sha256,
        image_bucket,
        image_object_key,
        prediction_class,
        probabilities,
        model_name,
        model_version,
        confidence,
        quality_status,
        quality_messages,
        model_response,
        report_bucket,
        report_object_key
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s::jsonb,
        %s,
        %s,
        %s,
        %s,
        %s::jsonb,
        %s::jsonb,
        %s,
        %s
    );
    """

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                insert_query,
                (
                    study_id,
                    created_at,
                    original_filename,
                    content_type,
                    len(image_bytes),
                    checksum_sha256,
                    MINIO_BUCKET_NAME,
                    stored_image_object_key,
                    prediction_class,
                    json.dumps(probabilities),
                    model_name,
                    model_version,
                    confidence,
                    quality_status,
                    json.dumps(quality_messages),
                    json.dumps(prediction),
                    MINIO_BUCKET_NAME,
                    report_object_key,
                ),
            )
        connection.commit()

    generated_events = []
    if prediction_class == "COVID-19":
        generated_events.append(
            record_quality_event(
                source="radiology",
                severity="high",
                event_type="clinical_alert",
                message="Radiografia clasificada como COVID-19: requiere revision prioritaria.",
                metadata={"study_id": study_id, "confidence": confidence},
            )
        )
    if confidence < 0.55:
        generated_events.append(
            record_quality_event(
                source="radiology",
                severity="medium",
                event_type="low_model_confidence",
                message="Prediccion radiologica con baja confianza.",
                metadata={"study_id": study_id, "confidence": confidence},
            )
        )
    if quality_messages:
        generated_events.append(
            record_quality_event(
                source="radiology",
                severity="medium",
                event_type="image_quality",
                message="Estudio radiologico con advertencias de calidad.",
                metadata={"study_id": study_id, "messages": quality_messages},
            )
        )

    return {
        "study_id": study_id,
        "created_at": created_at.isoformat(),
        "quality_status": quality_status,
        "quality_messages": quality_messages,
        "image_bucket": MINIO_BUCKET_NAME,
        "image_object_key": stored_image_object_key,
        "report_bucket": MINIO_BUCKET_NAME,
        "report_object_key": report_object_key,
        "events": generated_events,
    }


def persist_triage_record(payload: dict[str, Any], assessment: dict[str, Any]) -> dict[str, Any]:
    record_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    object_key = f"triage-reports/{record_id}.json"

    report_document = {
        "triage_id": record_id,
        "created_at": created_at.isoformat(),
        "request": payload,
        "assessment": assessment,
    }

    minio_client = get_minio_client()
    validate_minio_bucket()
    minio_client.put_object(
        Bucket=MINIO_BUCKET_NAME,
        Key=object_key,
        Body=json.dumps(report_document).encode("utf-8"),
        ContentType="application/json",
    )

    insert_query = """
    INSERT INTO triage_records (
        id,
        created_at,
        request_payload,
        model_response,
        risk_level,
        recommended_priority,
        score,
        confidence,
        report_bucket,
        report_object_key
    )
    VALUES (
        %s,
        %s,
        %s::jsonb,
        %s::jsonb,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    );
    """

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                insert_query,
                (
                    record_id,
                    created_at,
                    json.dumps(payload),
                    json.dumps(assessment),
                    str(assessment.get("risk_level", "unknown")),
                    str(assessment.get("recommended_priority", "unknown")),
                    int(assessment.get("score", 0) or 0),
                    float(assessment.get("confidence", 0) or 0),
                    MINIO_BUCKET_NAME,
                    object_key,
                ),
            )
        connection.commit()

    return {
        "triage_id": record_id,
        "created_at": created_at.isoformat(),
        "report_bucket": MINIO_BUCKET_NAME,
        "report_object_key": object_key,
    }


def fetch_recent_triage(limit: int) -> list[dict[str, Any]]:
    query = """
    SELECT
        id,
        created_at,
        risk_level,
        recommended_priority,
        score,
        confidence,
        report_bucket,
        report_object_key
    FROM triage_records
    ORDER BY created_at DESC
    LIMIT %s;
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

    return [
        {
            "triage_id": row["id"],
            "created_at": row["created_at"].isoformat(),
            "risk_level": row["risk_level"],
            "recommended_priority": row["recommended_priority"],
            "score": row["score"],
            "confidence": row["confidence"],
            "report_bucket": row["report_bucket"],
            "report_object_key": row["report_object_key"],
        }
        for row in rows
    ]


def fetch_triage_record(triage_id: str) -> dict[str, Any] | None:
    query = """
    SELECT
        id,
        created_at,
        request_payload,
        model_response,
        risk_level,
        recommended_priority,
        score,
        confidence,
        report_bucket,
        report_object_key
    FROM triage_records
    WHERE id = %s;
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (triage_id,))
            row = cursor.fetchone()

    if not row:
        return None

    return {
        "triage_id": row["id"],
        "created_at": row["created_at"].isoformat(),
        "request": row["request_payload"],
        "assessment": row["model_response"],
        "risk_level": row["risk_level"],
        "recommended_priority": row["recommended_priority"],
        "score": row["score"],
        "confidence": row["confidence"],
        "report_bucket": row["report_bucket"],
        "report_object_key": row["report_object_key"],
    }


def load_report_from_minio(triage_id: str) -> dict[str, Any]:
    record = fetch_triage_record(triage_id)
    if not record:
        raise KeyError(triage_id)

    minio_client = get_minio_client()
    response = minio_client.get_object(
        Bucket=record["report_bucket"],
        Key=record["report_object_key"],
    )
    return json.loads(response["Body"].read().decode("utf-8"))


def fetch_recent_studies(limit: int) -> list[dict[str, Any]]:
    query = """
    SELECT
        id,
        created_at,
        original_filename,
        content_type,
        file_size_bytes,
        image_bucket,
        image_object_key,
        prediction_class,
        probabilities,
        model_name,
        model_version,
        confidence,
        quality_status,
        quality_messages,
        report_bucket,
        report_object_key
    FROM radiology_studies
    ORDER BY created_at DESC
    LIMIT %s;
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

    return [
        {
            "study_id": row["id"],
            "created_at": row["created_at"].isoformat(),
            "original_filename": row["original_filename"],
            "content_type": row["content_type"],
            "file_size_bytes": row["file_size_bytes"],
            "image_bucket": row["image_bucket"],
            "image_object_key": row["image_object_key"],
            "prediction_class": row["prediction_class"],
            "probabilities": row["probabilities"],
            "model_name": row["model_name"],
            "model_version": row["model_version"],
            "confidence": row["confidence"],
            "quality_status": row["quality_status"],
            "quality_messages": row["quality_messages"],
            "report_bucket": row["report_bucket"],
            "report_object_key": row["report_object_key"],
        }
        for row in rows
    ]


def fetch_study_record(study_id: str) -> dict[str, Any] | None:
    query = """
    SELECT
        id,
        created_at,
        original_filename,
        content_type,
        file_size_bytes,
        checksum_sha256,
        image_bucket,
        image_object_key,
        prediction_class,
        probabilities,
        model_name,
        model_version,
        confidence,
        quality_status,
        quality_messages,
        model_response,
        report_bucket,
        report_object_key
    FROM radiology_studies
    WHERE id = %s;
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (study_id,))
            row = cursor.fetchone()

    if not row:
        return None

    return {
        "study_id": row["id"],
        "created_at": row["created_at"].isoformat(),
        "original_filename": row["original_filename"],
        "content_type": row["content_type"],
        "file_size_bytes": row["file_size_bytes"],
        "checksum_sha256": row["checksum_sha256"],
        "image_bucket": row["image_bucket"],
        "image_object_key": row["image_object_key"],
        "prediction_class": row["prediction_class"],
        "probabilities": row["probabilities"],
        "model": {
            "name": row["model_name"],
            "version": row["model_version"],
            "response": row["model_response"],
        },
        "confidence": row["confidence"],
        "quality_status": row["quality_status"],
        "quality_messages": row["quality_messages"],
        "report_bucket": row["report_bucket"],
        "report_object_key": row["report_object_key"],
    }


def load_study_report_from_minio(study_id: str) -> dict[str, Any]:
    record = fetch_study_record(study_id)
    if not record:
        raise KeyError(study_id)

    minio_client = get_minio_client()
    response = minio_client.get_object(
        Bucket=record["report_bucket"],
        Key=record["report_object_key"],
    )
    return json.loads(response["Body"].read().decode("utf-8"))


def fetch_quality_events(limit: int) -> list[dict[str, Any]]:
    query = """
    SELECT
        id,
        created_at,
        source,
        severity,
        event_type,
        message,
        metadata,
        resolved
    FROM quality_events
    ORDER BY created_at DESC
    LIMIT %s;
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

    return [
        {
            "event_id": row["id"],
            "created_at": row["created_at"].isoformat(),
            "source": row["source"],
            "severity": row["severity"],
            "event_type": row["event_type"],
            "message": row["message"],
            "metadata": row["metadata"],
            "resolved": row["resolved"],
        }
        for row in rows
    ]


def fetch_platform_metrics() -> dict[str, Any]:
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_studies,
                    COUNT(*) FILTER (WHERE prediction_class = 'Sana') AS healthy_count,
                    COUNT(*) FILTER (WHERE prediction_class = 'Neumonia') AS pneumonia_count,
                    COUNT(*) FILTER (WHERE prediction_class = 'COVID-19') AS covid_count,
                    COUNT(*) FILTER (WHERE quality_status <> 'accepted') AS warning_count,
                    COALESCE(AVG(confidence), 0) AS average_confidence,
                    MAX(created_at) AS last_study_at
                FROM radiology_studies;
                """
            )
            radiology = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) AS total_triage FROM triage_records;")
            triage = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    id,
                    created_at,
                    finished_at,
                    status,
                    input_uri,
                    processed_count,
                    rejected_count,
                    report_bucket,
                    report_object_key,
                    metadata
                FROM pipeline_runs
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )
            pipeline = cursor.fetchone()

            cursor.execute(
                """
                SELECT severity, COUNT(*) AS count
                FROM quality_events
                WHERE resolved = FALSE
                GROUP BY severity
                ORDER BY severity;
                """
            )
            severity_rows = cursor.fetchall()

    last_study_at = radiology["last_study_at"]
    latest_pipeline = None
    if pipeline:
        latest_pipeline = {
            "run_id": pipeline["id"],
            "created_at": pipeline["created_at"].isoformat(),
            "finished_at": pipeline["finished_at"].isoformat() if pipeline["finished_at"] else None,
            "status": pipeline["status"],
            "input_uri": pipeline["input_uri"],
            "processed_count": pipeline["processed_count"],
            "rejected_count": pipeline["rejected_count"],
            "report_bucket": pipeline["report_bucket"],
            "report_object_key": pipeline["report_object_key"],
            "metadata": pipeline["metadata"],
        }

    return {
        "radiology": {
            "total_studies": radiology["total_studies"],
            "class_distribution": {
                "Sana": radiology["healthy_count"],
                "Neumonia": radiology["pneumonia_count"],
                "COVID-19": radiology["covid_count"],
            },
            "warning_count": radiology["warning_count"],
            "average_confidence": round(float(radiology["average_confidence"] or 0), 4),
            "last_study_at": last_study_at.isoformat() if last_study_at else None,
        },
        "triage": {
            "total_records": triage["total_triage"],
        },
        "pipeline": {
            "latest_run": latest_pipeline,
        },
        "quality": {
            "open_events_by_severity": {
                row["severity"]: row["count"]
                for row in severity_rows
            }
        },
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    postgres_status = await run_in_threadpool(get_postgres_status)
    minio_status = await run_in_threadpool(get_minio_status)
    status = "ok"
    if postgres_status != "ok" or minio_status != "ok":
        status = "degraded"

    return {
        "status": status,
        "services": {
            "inference_engine": "embedded",
            "triage_model": triage_model.model_status(),
            "postgres": postgres_status,
            "minio": minio_status,
            "spark": SPARK_MASTER_URL,
        },
        "storage": {
            "postgres_database": POSTGRES_DB,
            "minio_endpoint": MINIO_ENDPOINT or "not-configured",
            "minio_region": MINIO_REGION,
            "minio_bucket": MINIO_BUCKET_NAME,
        },
    }


@app.post("/triage")
async def triage(payload: TriageRequest) -> dict[str, Any]:
    assessment = compute_triage(payload)

    try:
        storage_result = await run_in_threadpool(
            persist_triage_record,
            payload.model_dump(),
            assessment,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist triage result: {exc}",
        ) from exc

    events: list[dict[str, Any]] = []
    risk_level = assessment.get("risk_level", "unknown")
    confidence = float(assessment.get("confidence", 0) or 0)
    triage_id = storage_result["triage_id"]

    if risk_level == "critical":
        events.append(
            await run_in_threadpool(
                record_quality_event,
                source="triage",
                severity="high",
                event_type="clinical_alert",
                message="Triaje clasificado como critico: requiere atencion inmediata.",
                metadata={"triage_id": triage_id, "confidence": confidence},
            )
        )
    if confidence and confidence < 0.55:
        events.append(
            await run_in_threadpool(
                record_quality_event,
                source="triage",
                severity="medium",
                event_type="low_model_confidence",
                message="Triaje con baja confianza del modelo.",
                metadata={"triage_id": triage_id, "confidence": confidence},
            )
        )

    return {
        "status": "accepted",
        "triage_id": triage_id,
        "created_at": storage_result["created_at"],
        "patient_assessment": assessment,
        "storage": {
            "postgres_database": POSTGRES_DB,
            "minio_bucket": storage_result["report_bucket"],
            "minio_object_key": storage_result["report_object_key"],
        },
        "events": events,
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    source_object_key: str | None = Form(default=None),
) -> dict[str, Any]:
    try:
        image_bytes = await read_and_validate_prediction_file(file)
        prediction = await run_in_threadpool(infer_xray_prediction, image_bytes)
        storage_result = await run_in_threadpool(
            persist_radiology_study,
            original_filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            image_bytes=image_bytes,
            prediction=prediction,
            source_object_key=source_object_key,
        )
        return {
            **prediction,
            "study_id": storage_result["study_id"],
            "created_at": storage_result["created_at"],
            "quality_status": storage_result["quality_status"],
            "storage": {
                "postgres_database": POSTGRES_DB,
                "minio_bucket": storage_result["report_bucket"],
                "image_object_key": storage_result["image_object_key"],
                "report_object_key": storage_result["report_object_key"],
            },
            "events": storage_result["events"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed") from exc
    finally:
        await file.close()


@app.get("/studies/history")
async def studies_history(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, Any]:
    records = await run_in_threadpool(fetch_recent_studies, limit)
    return {
        "count": len(records),
        "items": records,
    }


@app.get("/studies/{study_id}")
async def study_detail(study_id: str) -> dict[str, Any]:
    record = await run_in_threadpool(fetch_study_record, study_id)
    if not record:
        raise HTTPException(status_code=404, detail="Radiology study not found")
    return record


@app.get("/studies/{study_id}/report")
async def study_report(study_id: str) -> dict[str, Any]:
    try:
        report = await run_in_threadpool(load_study_report_from_minio, study_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Radiology study not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load report: {exc}") from exc
    return report


@app.get("/quality/events")
async def quality_events(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, Any]:
    events = await run_in_threadpool(fetch_quality_events, limit)
    return {
        "count": len(events),
        "items": events,
    }


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    return await run_in_threadpool(fetch_platform_metrics)


@app.get("/triage/history")
async def triage_history(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, Any]:
    records = await run_in_threadpool(fetch_recent_triage, limit)
    return {
        "count": len(records),
        "items": records,
    }


@app.get("/triage/{triage_id}")
async def triage_detail(triage_id: str) -> dict[str, Any]:
    record = await run_in_threadpool(fetch_triage_record, triage_id)
    if not record:
        raise HTTPException(status_code=404, detail="Triage record not found")
    return record


@app.get("/triage/{triage_id}/report")
async def triage_report(triage_id: str) -> dict[str, Any]:
    try:
        report = await run_in_threadpool(load_report_from_minio, triage_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Triage record not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load report: {exc}") from exc
    return report
