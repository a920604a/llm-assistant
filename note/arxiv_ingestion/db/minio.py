import boto3
from arxiv_ingestion.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
)
from botocore.client import Config
from logger import get_logger

logger = get_logger(__name__)


# 初始化 MinIO (S3) 客戶端
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


# 建立 bucket（若不存在）
def create_note_bucket():
    logger.info(f"MINIO_ENDPOINT {MINIO_ENDPOINT}")
    logger.info(f"MINIO_ACCESS_KEY {MINIO_ACCESS_KEY}")
    logger.info(f"MINIO_SECRET_KEY {MINIO_SECRET_KEY}")

    buckets = [b["Name"] for b in s3_client.list_buckets()["Buckets"]]
    logger.info(f"buckets {buckets}")
    if MINIO_BUCKET not in buckets:
        s3_client.create_bucket(Bucket=MINIO_BUCKET)


def s3_file_exists(bucket: str, object_name: str) -> bool:
    """檢查 MinIO / S3 上是否有該檔案"""
    try:
        s3_client.head_object(Bucket=bucket, Key=object_name)
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise
