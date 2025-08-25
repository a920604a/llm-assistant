import boto3
from botocore.client import Config
from config import MINIO_ACCESS_KEY, MINIO_BUCKET, MINIO_ENDPOINT, MINIO_SECRET_KEY

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
    buckets = [b["Name"] for b in s3_client.list_buckets()["Buckets"]]
    if MINIO_BUCKET not in buckets:
        s3_client.create_bucket(Bucket=MINIO_BUCKET)
