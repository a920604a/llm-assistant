import os
from dotenv import load_dotenv


load_dotenv()

MODEL_NAME="phi3:latest" #  "gpt-oss:20b, phi3:latest gemma:2b

# === 基本設定 ===
OLLAMA_API_URL = "http://ollama:11434"
QDRANT_URL = "http://note-qdrant:6333"
COLLECTION_NAME = "notes_collection"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@note-db:5432/note")


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://note-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "note")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "note123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "notes-md")


