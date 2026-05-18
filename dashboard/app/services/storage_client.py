from __future__ import annotations

from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import ObjectStorageSettings


class StorageError(RuntimeError):
    pass


class StorageClient:
    def __init__(self, settings: ObjectStorageSettings):
        self._settings = settings

    @property
    def bucket(self) -> str:
        return self._settings.bucket_name

    def _build_client(self):
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

    def upload_image(self, *, file_bytes: bytes, extension: str, mime_type: str) -> str:
        try:
            client = self._build_client()
            self._ensure_bucket(client)
            object_key = self._unique_key(client, extension)
            client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=file_bytes,
                ContentType=mime_type,
            )
            return object_key
        except (ClientError, BotoCoreError) as exc:
            raise StorageError("No se pudo subir la imagen a MinIO.") from exc

    def _ensure_bucket(self, client) -> None:
        try:
            client.head_bucket(Bucket=self.bucket)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code not in {"404", "NoSuchBucket", "NotFound"}:
                raise
            client.create_bucket(Bucket=self.bucket)

    def _unique_key(self, client, extension: str) -> str:
        for _ in range(10):
            object_key = f"uploads/{uuid4().hex}.{extension}"
            if not self._object_exists(client, object_key):
                return object_key
        raise StorageError("No se pudo generar un nombre unico para la imagen.")

    def _object_exists(self, client, object_key: str) -> bool:
        try:
            client.head_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
