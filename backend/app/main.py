import json
import os
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
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, ImageStat, UnidentifiedImageError
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "hospital_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me_postgres_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital_db")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "")
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


def compute_triage(payload: TriageRequest) -> dict[str, Any]:
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
        "model_name": "hospital-triage-embedded",
        "risk_level": risk_level,
        "recommended_priority": recommended_priority,
        "confidence": round(0.65 + (score / 200), 2),
        "score": score,
    }


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

    return {
        "class": predicted_class,
        "probabilities": probabilities,
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
                    assessment.get("risk_level", "unknown"),
                    assessment.get("recommended_priority", "unknown"),
                    int(assessment.get("score", 0)),
                    float(assessment.get("confidence", 0)),
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

    return {
        "status": "accepted",
        "triage_id": storage_result["triage_id"],
        "created_at": storage_result["created_at"],
        "patient_assessment": assessment,
        "storage": {
            "postgres_database": POSTGRES_DB,
            "minio_bucket": storage_result["report_bucket"],
            "minio_object_key": storage_result["report_object_key"],
        },
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        image_bytes = await read_and_validate_prediction_file(file)
        return await run_in_threadpool(infer_xray_prediction, image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed") from exc
    finally:
        await file.close()


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
