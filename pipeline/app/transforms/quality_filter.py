from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, lit, trim


@dataclass(frozen=True)
class PartitionResult:
    accepted: DataFrame
    rejected: DataFrame
    duplicate_object_keys: list[str]


def normalize(df: DataFrame, required_columns: tuple[str, ...]) -> DataFrame:
    return df.select([trim(col(column)).alias(column) for column in required_columns])


def detect_duplicate_object_keys(df: DataFrame) -> list[str]:
    duplicates = (
        df.groupBy("image_object_key")
        .agg(count("*").alias("records"))
        .filter((col("image_object_key") != "") & (col("records") > 1))
        .collect()
    )
    return [row["image_object_key"] for row in duplicates]


def partition(
    df: DataFrame,
    required_columns: tuple[str, ...],
    valid_labels: tuple[str, ...],
) -> PartitionResult:
    duplicate_keys = detect_duplicate_object_keys(df)
    condition = lit(True)
    for column in required_columns:
        condition = condition & col(column).isNotNull() & (col(column) != "")
    condition = condition & col("label").isin(list(valid_labels))
    if duplicate_keys:
        condition = condition & ~col("image_object_key").isin(duplicate_keys)
    return PartitionResult(
        accepted=df.filter(condition),
        rejected=df.filter(~condition),
        duplicate_object_keys=duplicate_keys,
    )
