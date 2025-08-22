import os

from pydantic import BaseSettings, Field

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL_NAME = "gpt-oss:20b"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")


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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
