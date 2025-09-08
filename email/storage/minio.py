import sys

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from config import settings

# 初始化 MinIO (S3) 客戶端
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.MINIO_ENDPOINT,
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def create_bucket(bucket_name):
    try:
        buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
        if bucket_name in buckets:
            print(f"[INFO] Bucket '{bucket_name}' already exists.")
        else:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"[INFO] Bucket '{bucket_name}' created successfully.")
    except EndpointConnectionError:
        print(
            f"[ERROR] Cannot connect to MinIO at {settings.MINIO_ENDPOINT}",
            file=sys.stderr,
        )
        sys.exit(1)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"[INFO] Bucket '{bucket_name}' already exists (handled).")
            return
        else:
            print(f"[ERROR] Failed to create bucket '{bucket_name}': {e}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("[INFO] Starting MinIO bucket creation...")
    create_bucket(settings.MINIO_NOTE_BUCKET)
    create_bucket(settings.MINIO_SUMMARY_BUCKET)
    print("[INFO] MinIO bucket creation finished.")
