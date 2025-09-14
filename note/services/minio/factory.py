from functools import lru_cache

from config import get_settings
from services.minio.client import MinioClient


@lru_cache(maxsize=1)
def make_minio_client() -> MinioClient:
    """
    Create and return a singleton Ollama client instance.

    Returns:
        OllamaClient: Configured Ollama client
    """
    settings = get_settings()
    return MinioClient(settings)
