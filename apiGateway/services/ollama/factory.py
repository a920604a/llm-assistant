from functools import lru_cache

from config import get_settings
from services.ollama.client import OllamaClient


@lru_cache(maxsize=1)
def make_ollama_client() -> OllamaClient:
    """
    Create and return a singleton Ollama client instance.

    Returns:
        OllamaClient: Configured Ollama client
    """
    settings = get_settings()
    return OllamaClient(settings)
