import os

from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

MODEL_NAME = "gpt-oss:20b"

UPLOAD_DIR = "/data/uploaded_files"
# === 基本設定 ===
OLLAMA_API_URL = "http://ollama:11434"
QDRANT_URL = "http://note-qdrant:6333"
COLLECTION_NAME = "notes_collection"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://note-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "note")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "note123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "notes-md")
