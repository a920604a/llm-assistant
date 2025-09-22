import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
QDRANT_BATCH_SIZE = 200
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")


PDF_CACHE_DIR = "/data/arxiv_pdfs"
COLLECTION_NAME = "arxiv_collection"
QDRANT_URL = "http://note-qdrant:6333"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")

MINIO_ENDPOINT = os.getenv("MINIO__ENDPOINT", "http://note-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO__ACCESS_KEY", "note")
MINIO_SECRET_KEY = os.getenv("MINIO__SECRET_KEY", "note123")
MINIO_BUCKET = os.getenv("MINIO__BUCKET", "notes-md")

# CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")


class DefaultSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
        frozen = True


class ArxivSettings(DefaultSettings):
    api_base_url: str = "https://export.arxiv.org/api/query"
    cache_dir: str = PDF_CACHE_DIR
    # base_url: str = "https://export.arxiv.org/api/query"
    pdf_cache_dir: str = PDF_CACHE_DIR
    rate_limit_delay: float = 4.0  # seconds between requests
    timeout_seconds: int = 30
    max_results: int = 100
    search_category: str = "cs.AI"  # 預設抓 cs.AI 分類
