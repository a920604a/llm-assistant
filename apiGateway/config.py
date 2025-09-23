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


class Settings(BaseConfigSettings):
    app_version: str = "0.1.0"
    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"
    service_name: str = "API Gateway"

    # 外部服務 URL
    DATABASE_URL: str = "postgresql://user:password@note-db:5432/note"
    REDIS_URL: str = "redis://redis:6379/2"  # for user cache
    NOTE_API_URL: str = "http://noteserver:8000"
    SPEECH_API_URL: str = "http://imageserver:8000"
    IMAGE_API_URL: str = "http://speechserver:8000"
    OLLAMA_API_URL: str = "http://ollama:11434"
    OLLAMA_TIMEOUT: int = 300

    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)

    # 模型名稱
    SUMMARY_MODEL_NAME: str = "gpt-oss:20b"

    # Firebase key path
    FIRBASE_KEY_PATH: str = "/app"


# **全局唯一實例**
settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return settings
