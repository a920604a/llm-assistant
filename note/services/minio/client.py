import boto3
from botocore.client import Config
from config import Settings
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class MinioClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def create_note_bucket(self):
        buckets = [b["Name"] for b in self.list_buckets()["Buckets"]]
        if self.settings.MINIO_BUCKET not in buckets:
            self.client.create_bucket(Bucket=self.settings.MINIO_BUCKET)

    def list_buckets(self):
        return self.client.list_buckets()
