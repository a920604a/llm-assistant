import os
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL_NAME = "gpt-oss:20b"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")
COLLECTION_NAME = "arxiv_collection"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Firebase Key
FIREBASE_KEY_PATH = "/app"


class Settings(BaseSettings):
    # Celery / Redis
    REDIS_BROKER: str = Field(
        default="redis://localhost:6379/0", env="CELERY_BROKER_URL"
    )
    REDIS_BACKEND: str = Field(default="redis://redis:6379/3", env="REDIS_BACKEND")

    # 郵件設定
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")  # 必填
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")  # 必填
    MAIL_FROM: str = Field(..., env="MAIL_FROM")  # 必填
    MAIL_SERVER: str = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_TLS: bool = Field(default=True, env="MAIL_TLS")
    MAIL_SSL: bool = Field(default=False, env="MAIL_SSL")

    # MINIO 常量，用 ClassVar 標記非 model field
    MINIO_ENDPOINT: ClassVar[str] = os.getenv(
        "MINIO_ENDPOINT", "http://note-minio:9000"
    )
    MINIO_ACCESS_KEY: ClassVar[str] = os.getenv("MINIO_ACCESS_KEY", "note")
    MINIO_SECRET_KEY: ClassVar[str] = os.getenv("MINIO_SECRET_KEY", "note123")
    MINIO_NOTE_BUCKET: ClassVar[str] = os.getenv("MINIO_BUCKET", "notes-md")
    MINIO_SUMMARY_BUCKET: ClassVar[str] = os.getenv(
        "MINIO_SUMMARY_BUCKET", "daily-summary"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
