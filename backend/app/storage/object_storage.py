from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.config import ObjectStorageSettings, get_settings


class ObjectStorageError(RuntimeError):
    pass


class ObjectStorageUnavailable(ObjectStorageError):
    pass


class ObjectStorage:
    """S3-compatible object storage adapter (MinIO).

    Single responsibility: serialize bytes/JSON to and from the configured bucket.
    Connection state is created per call so the adapter is safe across worker threads.
    """

    def __init__(self, settings: ObjectStorageSettings):
        self._settings = settings

    @property
    def bucket(self) -> str:
        return self._settings.bucket_name

    def _build_client(self):
        return boto3.client(
            service_name="s3",
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
        client = self._build_client()
        try:
            client.head_bucket(Bucket=self._settings.bucket_name)
        except NoCredentialsError as exc:
            raise ObjectStorageError("MinIO credentials are not configured") from exc
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in {"404", "NoSuchBucket", "NotFound"} and self._settings.auto_create_bucket:
                self._create_bucket(client)
                return
            raise ObjectStorageUnavailable(
                f"MinIO bucket '{self._settings.bucket_name}' is not accessible: {error_code or exc}"
            ) from exc

    def _create_bucket(self, client) -> None:
        if self._settings.region == "us-east-1":
            client.create_bucket(Bucket=self._settings.bucket_name)
            return
        client.create_bucket(
            Bucket=self._settings.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": self._settings.region},
        )

    def put_bytes(self, object_key: str, body: bytes, content_type: str) -> None:
        client = self._build_client()
        client.put_object(
            Bucket=self._settings.bucket_name,
            Key=object_key,
            Body=body,
            ContentType=content_type,
        )

    def put_json(self, object_key: str, document: dict[str, Any]) -> None:
        self.put_bytes(
            object_key=object_key,
            body=json.dumps(document).encode("utf-8"),
            content_type="application/json",
        )

    def get_json(self, object_key: str) -> dict[str, Any]:
        client = self._build_client()
        response = client.get_object(Bucket=self._settings.bucket_name, Key=object_key)
        return json.loads(response["Body"].read().decode("utf-8"))


def build_object_storage() -> ObjectStorage:
    return ObjectStorage(get_settings().object_storage)
