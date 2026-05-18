"""Spark entrypoint. Pure orchestration — every responsibility delegated to
its own module under app/."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.spark_factory import build_spark_session
from app.reports.run_report import build_failure_report, build_success_report
from app.transforms.quality_filter import normalize, partition
from app.validators.csv_schema import assert_columns_present
from app.writers.minio_writer import MinioWriter
from app.writers.postgres_writer import PostgresWriter


def main() -> None:
    configure_logging()
    logger = get_logger("pipeline.radiology")
    settings = get_settings()

    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    spark = build_spark_session()
    minio = MinioWriter(settings.object_storage)
    postgres = PostgresWriter(settings.postgres)

    try:
        logger.info("pipeline_started", extra={"run_id": run_id, "input_uri": settings.paths.input_path})
        raw_df = spark.read.option("header", True).csv(settings.paths.input_path)
        assert_columns_present(raw_df.columns, settings.schema_rules.required_columns)

        normalized = normalize(raw_df, settings.schema_rules.required_columns)
        partitioned = partition(
            normalized,
            settings.schema_rules.required_columns,
            settings.schema_rules.valid_labels,
        )

        processed_count = partitioned.accepted.count()
        rejected_count = partitioned.rejected.count()
        partitioned.accepted.write.mode("overwrite").json(settings.paths.output_path)

        class_distribution = {
            row["label"]: row["count"]
            for row in partitioned.accepted.groupBy("label").count().collect()
        }
        rejected_samples = [row.asDict() for row in partitioned.rejected.limit(25).collect()]

        report = build_success_report(
            run_id=run_id,
            created_at=created_at,
            finished_at=datetime.now(timezone.utc),
            input_uri=settings.paths.input_path,
            output_uri=settings.paths.output_path,
            processed_count=processed_count,
            rejected_count=rejected_count,
            required_columns=settings.schema_rules.required_columns,
            valid_labels=settings.schema_rules.valid_labels,
            duplicate_object_keys=partitioned.duplicate_object_keys,
            class_distribution=class_distribution,
            rejected_samples=rejected_samples,
        )

        report_object_key = minio.write_report(report)
        postgres.persist_run(report=report, report_object_key=report_object_key, bucket=minio.bucket)
        if rejected_count:
            postgres.record_quality_event(
                report=report,
                severity="medium",
                event_type="data_quality_rejections",
                message="El pipeline rechazo registros por campos incompletos, etiquetas invalidas o duplicados.",
            )

        logger.info("pipeline_completed", extra={
            "run_id": run_id,
            "status": report["status"],
            "processed_count": processed_count,
            "rejected_count": rejected_count,
        })
        print(json.dumps(report, indent=2))

    except Exception as exc:
        logger.exception("pipeline_failed", extra={"run_id": run_id})
        report = build_failure_report(
            run_id=run_id,
            created_at=created_at,
            finished_at=datetime.now(timezone.utc),
            input_uri=settings.paths.input_path,
            output_uri=settings.paths.output_path,
            error=str(exc),
        )
        try:
            report_object_key = minio.write_report(report)
            postgres.persist_run(report=report, report_object_key=report_object_key, bucket=minio.bucket)
            postgres.record_quality_event(
                report=report,
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
