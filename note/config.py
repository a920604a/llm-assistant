from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class BaseConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        extra="ignore",
        frozen=True,
        env_nested_delimiter="__",
        case_sensitive=False,
    )


class RedisSettings(BaseConfigSettings):
    url: str  # 完整 URL，例如 redis://redis:6379/2
    ttl_hour: int = 6
    decode_responses: bool = True
    socket_timeout: int = 30
    socket_connect_timeout: int = 30


class Settings(BaseConfigSettings):
    app_version: str = "0.1.0"
    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"
    service_name: str = "Note RAG api"

    # 外部服務 URL
    DATABASE_URL: str = "postgresql://user:password@note-db:5432/note"

    redis_user: RedisSettings = RedisSettings(url="redis://redis:6379/2")
    redis_paper: RedisSettings = RedisSettings(url="redis://redis:6379/5")

    REDIS_TTL_HOUR: int = 6

    OLLAMA_API_URL: str = "http://ollama:11434"
    OLLAMA_TIMEOUT: int = 300
    QDRANT_URL: str = "http://note-qdrant:6333"

    MINIO_ENDPOINT: str = "http://note-minio:9000"
    MINIO_ACCESS_KEY: str = "note"
    MINIO_SECRET_KEY: str = "note123"
    MINIO_BUCKET: str = "notes-md"

    # 模型名稱
    MODEL_NAME: str = "gpt-oss:20b"

    COLLECTION_NAME: str = "arxiv_collection"

    UPLOAD_DIR: str = "/data/uploaded_files"


@lru_cache
def get_settings() -> Settings:
    return Settings()
