from __future__ import annotations

from pyspark.sql import SparkSession


def build_spark_session(app_name: str = "hospital-radiology-pipeline") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
