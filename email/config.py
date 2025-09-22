import os

from pydantic import Field
from pydantic_settings import BaseSettings

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")
COLLECTION_NAME = "arxiv_collection"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Firebase Key
FIREBASE_KEY_PATH = "/app"


class Settings(BaseSettings):
    OLLAMA_API_URL: str = Field(
        default=os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    )
    MODEL_NAME: str = Field(default=os.getenv("MODEL_NAME", "gpt-oss:20b"))
    # 郵件設定
    MAIL_USERNAME: str = Field(default=os.getenv("MAIL_USERNAME"))
    MAIL_PASSWORD: str = Field(default=os.getenv("MAIL_PASSWORD"))
    MAIL_FROM: str = Field(default=os.getenv("MAIL_FROM"))
    MAIL_SERVER: str = Field(default=os.getenv("MAIL_SERVER", "smtp.gmail.com"))
    MAIL_PORT: int = Field(default=int(os.getenv("MAIL_PORT", 587)))
    MAIL_TLS: bool = Field(default=bool(int(os.getenv("MAIL_TLS", 1))))
    MAIL_SSL: bool = Field(default=bool(int(os.getenv("MAIL_SSL", 0))))

    MINIO_ENDPOINT: str = Field(
        default=os.getenv("MINIO__ENDPOINT", "http://note-minio:9000")
    )
    MINIO_ACCESS_KEY: str = Field(default=os.getenv("MINIO__ACCESS_KEY", "note"))
    MINIO_SECRET_KEY: str = Field(default=os.getenv("MINIO__SECRET_KEY", "note123"))
    MINIO_NOTE_BUCKET: str = Field(default=os.getenv("MINIO__BUCKET", "notes-md"))
    MINIO_SUMMARY_BUCKET: str = Field(
        default=os.getenv("MINIO__SUMMARY_BUCKET", "daily-summary")
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
