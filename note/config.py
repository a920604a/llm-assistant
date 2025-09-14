from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
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


class RedisUserSettings(BaseConfigSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="REDIS_USER__",
        case_sensitive=False,
        extra="ignore",
    )
    url: str
    ttl_hour: int = 6
    decode_responses: bool = True
    socket_timeout: int = 30
    socket_connect_timeout: int = 30


class RedisPaperSettings(BaseConfigSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="REDIS_PAPER__",
        case_sensitive=False,
        extra="ignore",
    )
    url: str
    ttl_hour: int = 6
    decode_responses: bool = True
    socket_timeout: int = 30
    socket_connect_timeout: int = 30


class LangfuseSettings(BaseConfigSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="LANGFUSE__",
        extra="ignore",
        frozen=True,
        case_sensitive=False,
    )

    public_key: str = ""
    secret_key: str = ""
    host: str = "http://localhost:3000"  # Self-hosted Langfuse URL
    enabled: bool = True
    flush_at: int = 15  # Number of events before flushing
    flush_interval: float = 1.0  # Seconds between flushes
    max_retries: int = 3
    timeout: int = 30
    debug: bool = False


class MinioSettings(BaseConfigSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="MINIO__",
        extra="ignore",
        frozen=True,
        case_sensitive=False,
    )

    endpoint: str = "http://note-minio:9000"
    access_key: str = "note"
    secret_key: str = "note123"
    bucket: str = "notes-md"
    summary_bucket: str = "daily-summary"


class Settings(BaseConfigSettings):
    app_version: str = "0.1.0"
    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"
    service_name: str = "Note RAG api"

    # 外部服務 URL
    DATABASE_URL: str = "postgresql://user:password@note-db:5432/note"

    redis_user: RedisUserSettings = RedisUserSettings(url="redis://redis:6379/2")
    redis_paper: RedisPaperSettings = RedisPaperSettings(url="redis://redis:6379/5")
    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)
    minio: MinioSettings = Field(default_factory=MinioSettings)

    REDIS_TTL_HOUR: int = 6

    OLLAMA_API_URL: str = "http://ollama:11434"
    OLLAMA_TIMEOUT: int = 300
    # 模型名稱
    MODEL_NAME: str = "gpt-oss:20b"
    # Qdrant
    QDRANT_URL: str = "http://note-qdrant:6333"
    COLLECTION_NAME: str = "arxiv_collection"

    UPLOAD_DIR: str = "/data/uploaded_files"


@lru_cache
def get_settings() -> Settings:
    return Settings()
