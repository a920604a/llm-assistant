import boto3
from botocore.client import Config
from config import MinioSettings, Settings
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class MinioClient:
    def __init__(self, settings: Settings):
        self.settings: MinioSettings = settings.minio
        self.client = boto3.client(
            "s3",
            endpoint_url=self.settings.endpoint,
            aws_access_key_id=self.settings.access_key,
            aws_secret_access_key=self.settings.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def create_note_bucket(self):
        buckets = [b["Name"] for b in self.list_buckets()["Buckets"]]
        if self.settings.bucket not in buckets:
            self.client.create_bucket(Bucket=self.settings.bucket)

    def list_buckets(self):
        return self.client.list_buckets()
