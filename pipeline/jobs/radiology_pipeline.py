import json
import os
from datetime import datetime, timezone
from uuid import uuid4

import boto3
import psycopg
from botocore.config import Config
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, lit, trim


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
PIPELINE_INPUT_PATH = os.getenv("PIPELINE_INPUT_PATH", "/data/incoming/radiology_studies.csv")
PIPELINE_OUTPUT_PATH = os.getenv("PIPELINE_OUTPUT_PATH", "/data/processed/radiology_clean")
VALID_LABELS = ["Sana", "Neumonia", "COVID-19"]
REQUIRED_COLUMNS = [
    "study_id",
    "patient_age",
    "patient_sex",
    "image_object_key",
    "label",
    "acquisition_date",
    "source",
]


def get_db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        connect_timeout=5,
    )


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
    except Exception:
        if MINIO_REGION == "us-east-1":
            client.create_bucket(Bucket=MINIO_BUCKET_NAME)
            return
        client.create_bucket(
            Bucket=MINIO_BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": MINIO_REGION},
        )


def write_report_to_minio(report: dict) -> str:
    client = get_minio_client()
    ensure_minio_bucket(client)
    object_key = f"pipeline-reports/{report['run_id']}.json"
    client.put_object(
        Bucket=MINIO_BUCKET_NAME,
        Key=object_key,
        Body=json.dumps(report, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    return object_key


def insert_pipeline_run(report: dict, report_object_key: str) -> None:
    query = """
    INSERT INTO pipeline_runs (
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
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb);
    """
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    report["run_id"],
                    report["created_at"],
                    report["finished_at"],
                    report["status"],
                    report["input_uri"],
                    report["processed_count"],
                    report["rejected_count"],
                    MINIO_BUCKET_NAME,
                    report_object_key,
                    json.dumps(report["metadata"]),
                ),
            )
        connection.commit()


def insert_quality_event(report: dict, severity: str, event_type: str, message: str) -> None:
    query = """
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
                query,
                (
                    str(uuid4()),
                    datetime.now(timezone.utc),
                    "pipeline",
                    severity,
                    event_type,
                    message,
                    json.dumps(
                        {
                            "run_id": report["run_id"],
                            "input_uri": report["input_uri"],
                            "rejected_count": report["rejected_count"],
                            "processed_count": report["processed_count"],
                        }
                    ),
                ),
            )
        connection.commit()


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("hospital-radiology-pipeline")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def main() -> None:
    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    spark = build_spark_session()

    try:
        raw_df = spark.read.option("header", True).csv(PIPELINE_INPUT_PATH)
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in raw_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        selected_df = raw_df.select(
            [trim(col(column)).alias(column) for column in REQUIRED_COLUMNS]
        )

        duplicate_rows = (
            selected_df.groupBy("image_object_key")
            .agg(count("*").alias("records"))
            .filter((col("image_object_key") != "") & (col("records") > 1))
            .collect()
        )
        duplicate_keys = [row["image_object_key"] for row in duplicate_rows]

        valid_condition = lit(True)
        for column in REQUIRED_COLUMNS:
            valid_condition = valid_condition & col(column).isNotNull() & (col(column) != "")
        valid_condition = valid_condition & col("label").isin(VALID_LABELS)
        if duplicate_keys:
            valid_condition = valid_condition & ~col("image_object_key").isin(duplicate_keys)

        processed_df = selected_df.filter(valid_condition)
        rejected_df = selected_df.filter(~valid_condition)

        processed_count = processed_df.count()
        rejected_count = rejected_df.count()
        processed_df.write.mode("overwrite").json(PIPELINE_OUTPUT_PATH)

        class_distribution = {
            row["label"]: row["count"]
            for row in processed_df.groupBy("label").count().collect()
        }
        rejected_samples = [
            row.asDict()
            for row in rejected_df.limit(25).collect()
        ]

        finished_at = datetime.now(timezone.utc)
        report = {
            "run_id": run_id,
            "created_at": created_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "status": "completed_with_warnings" if rejected_count else "completed",
            "input_uri": PIPELINE_INPUT_PATH,
            "output_uri": PIPELINE_OUTPUT_PATH,
            "processed_count": processed_count,
            "rejected_count": rejected_count,
            "metadata": {
                "required_columns": REQUIRED_COLUMNS,
                "valid_labels": VALID_LABELS,
                "duplicate_object_keys": duplicate_keys,
                "class_distribution": class_distribution,
                "rejected_samples": rejected_samples,
            },
        }

        report_object_key = write_report_to_minio(report)
        insert_pipeline_run(report, report_object_key)
        if rejected_count:
            insert_quality_event(
                report,
                severity="medium",
                event_type="data_quality_rejections",
                message="El pipeline rechazo registros por campos incompletos, etiquetas invalidas o duplicados.",
            )

        print(json.dumps(report, indent=2))
    except Exception as exc:
        finished_at = datetime.now(timezone.utc)
        report = {
            "run_id": run_id,
            "created_at": created_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "status": "failed",
            "input_uri": PIPELINE_INPUT_PATH,
            "output_uri": PIPELINE_OUTPUT_PATH,
            "processed_count": 0,
            "rejected_count": 0,
            "metadata": {"error": str(exc)},
        }
        try:
            report_object_key = write_report_to_minio(report)
            insert_pipeline_run(report, report_object_key)
            insert_quality_event(
                report,
                severity="high",
                event_type="pipeline_failure",
                message="El pipeline de datos fallo durante la ejecucion.",
            )
        finally:
            print(json.dumps(report, indent=2))
            raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
