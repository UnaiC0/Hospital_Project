from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.config import ObjectStorageSettings
from app.storage.object_storage import (
    ObjectStorage,
    ObjectStorageError,
    ObjectStorageUnavailable,
)


def make_settings(region: str = "us-east-1", auto_create: bool = False) -> ObjectStorageSettings:
    return ObjectStorageSettings(
        endpoint="http://minio:9000",
        access_key="a",
        secret_key="s",
        region=region,
        bucket_name="test-bucket",
        auto_create_bucket=auto_create,
    )


def client_error(code: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "x"}}, "HeadBucket")


@patch("app.storage.object_storage.boto3.client")
def test_ensure_bucket_succeeds_when_present(mock_boto):
    client = MagicMock()
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings())
    storage.ensure_bucket()
    client.head_bucket.assert_called_once_with(Bucket="test-bucket")
    client.create_bucket.assert_not_called()


@patch("app.storage.object_storage.boto3.client")
def test_ensure_bucket_auto_creates_when_missing_and_allowed(mock_boto):
    client = MagicMock()
    client.head_bucket.side_effect = client_error("404")
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings(auto_create=True))
    storage.ensure_bucket()
    client.create_bucket.assert_called_once_with(Bucket="test-bucket")


@patch("app.storage.object_storage.boto3.client")
def test_ensure_bucket_create_uses_location_constraint_for_non_default_region(mock_boto):
    client = MagicMock()
    client.head_bucket.side_effect = client_error("NoSuchBucket")
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings(region="eu-west-1", auto_create=True))
    storage.ensure_bucket()
    client.create_bucket.assert_called_once_with(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )


@patch("app.storage.object_storage.boto3.client")
def test_ensure_bucket_raises_when_missing_and_not_allowed(mock_boto):
    client = MagicMock()
    client.head_bucket.side_effect = client_error("404")
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings(auto_create=False))
    with pytest.raises(ObjectStorageUnavailable):
        storage.ensure_bucket()


@patch("app.storage.object_storage.boto3.client")
def test_ensure_bucket_credentials_error(mock_boto):
    client = MagicMock()
    client.head_bucket.side_effect = NoCredentialsError()
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings())
    with pytest.raises(ObjectStorageError, match="credentials"):
        storage.ensure_bucket()


@patch("app.storage.object_storage.boto3.client")
def test_put_bytes_delegates_to_s3(mock_boto):
    client = MagicMock()
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings())
    storage.put_bytes("k", b"hello", "text/plain")
    client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="k",
        Body=b"hello",
        ContentType="text/plain",
    )


@patch("app.storage.object_storage.boto3.client")
def test_put_json_serializes_payload(mock_boto):
    client = MagicMock()
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings())
    storage.put_json("k.json", {"a": 1})
    args = client.put_object.call_args.kwargs
    assert args["ContentType"] == "application/json"
    assert args["Body"] == b'{"a": 1}'


@patch("app.storage.object_storage.boto3.client")
def test_get_json_reads_and_parses(mock_boto):
    client = MagicMock()
    body = MagicMock()
    body.read.return_value = b'{"x": 2}'
    client.get_object.return_value = {"Body": body}
    mock_boto.return_value = client
    storage = ObjectStorage(make_settings())
    assert storage.get_json("k.json") == {"x": 2}
