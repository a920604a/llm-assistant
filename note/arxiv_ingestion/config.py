import os

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()

OLLAMA_API_URL = "http://ollama:11434"
MODEL_NAME = "gpt-oss:20b"


PDF_CACHE_DIR = "/data/arxiv_pdfs"
COLLECTION_NAME = "arxiv_collection"
QDRANT_URL = "http://note-qdrant:6333"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://note-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "note")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "note123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "notes-md")


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
    namespaces: dict = Field(
        default={
            "atom": "http://www.w3.org/2005/Atom",
            "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
    )
    rate_limit_delay: float = 4.0  # seconds between requests
    timeout_seconds: int = 30
    max_results: int = 100
    search_category: str = "cs.AI"  # 預設抓 cs.AI 分類
