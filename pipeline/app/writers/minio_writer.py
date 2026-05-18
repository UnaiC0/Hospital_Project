from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.config import Config

from app.core.config import ObjectStorageSettings


class MinioWriter:
    def __init__(self, settings: ObjectStorageSettings):
        self._settings = settings

    @property
    def bucket(self) -> str:
        return self._settings.bucket_name

    def _client(self):
        return boto3.client(
            "s3",
            endpoint_url=self._settings.endpoint,
            aws_access_key_id=self._settings.access_key,
            aws_secret_access_key=self._settings.secret_key,
            region_name=self._settings.region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def ensure_bucket(self) -> None:
        client = self._client()
        try:
            client.head_bucket(Bucket=self.bucket)
        except Exception:
            if self._settings.region == "us-east-1":
                client.create_bucket(Bucket=self.bucket)
                return
            client.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={"LocationConstraint": self._settings.region},
            )

    def write_report(self, report: dict[str, Any]) -> str:
        self.ensure_bucket()
        object_key = f"pipeline-reports/{report['run_id']}.json"
        self._client().put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=json.dumps(report, indent=2).encode("utf-8"),
            ContentType="application/json",
        )
        return object_key
