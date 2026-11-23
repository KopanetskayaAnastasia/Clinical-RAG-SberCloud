import os
import mimetypes

import boto3
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()


def get_s3_client():
    tenant_id = os.getenv("S3_TENANT_ID")
    key_id = os.getenv("S3_ACCESS_KEY_ID")
    key_secret = os.getenv("S3_SECRET_ACCESS_KEY")

    endpoint_url = os.getenv(
        "S3_ENDPOINT_URL",
        "https://s3.cloud.ru"
    )
    region = os.getenv("S3_REGION", "ru-central-1")

    if not all([tenant_id, key_id, key_secret]):
        raise ValueError(
            "Не заданы параметры доступа к Cloud.ru Object Storage"
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=f"{tenant_id}:{key_id}",
        aws_secret_access_key=key_secret,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"}
        )
    )


def upload_file_to_storage(
    file_path: str,
    object_name: str | None = None
) -> dict:
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not bucket_name:
        raise ValueError("Не задано имя S3_BUCKET_NAME")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    object_name = object_name or os.path.basename(file_path)

    content_type, _ = mimetypes.guess_type(object_name)

    if not content_type:
        content_type = "application/octet-stream"

    client = get_s3_client()

    try:
        with open(file_path, "rb") as file:
            client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=file,
                ContentType=content_type
            )

        return {
            "bucket": bucket_name,
            "object_name": object_name,
            "status": "uploaded"
        }

    finally:
        client.close()


def check_storage_connection():
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not bucket_name:
        raise ValueError("Не задано имя S3_BUCKET_NAME")

    client = get_s3_client()

    try:
        test_key = "_connection_test/connection_test.txt"

        client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body="Cloud.ru Object Storage connection successful".encode("utf-8"),
            ContentType="text/plain"
        )

        return {
            "bucket": bucket_name,
            "status": "connected",
            "test_object": test_key
        }

    finally:
        client.close()
