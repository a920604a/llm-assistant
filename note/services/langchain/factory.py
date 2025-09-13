from functools import lru_cache

from config import get_settings
from services.langchain.client import LangChainClient


@lru_cache(maxsize=1)
def make_langchain_client() -> LangChainClient:
    """
    Create and return a singleton langchain client instance.

    Returns:
        LangChainClient: Configured langchain client
    """
    settings = get_settings()
    return LangChainClient(settings)
