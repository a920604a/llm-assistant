import time

import boto3
from botocore.exceptions import EndpointConnectionError
from config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.MINIO_ENDPOINT,
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
)

print("Waiting for MinIO...")
while True:
    try:
        s3.list_buckets()
        print("MinIO is ready!")
        break
    except EndpointConnectionError:
        print("MinIO not ready yet, waiting 2s...")
        time.sleep(2)
