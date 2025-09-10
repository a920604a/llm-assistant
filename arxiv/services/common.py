from functools import lru_cache

from config import ArxivSettings
from services.arxiv_client import ArxivClient


@lru_cache(maxsize=1)
def get_cached_services() -> ArxivClient:
    settings = ArxivSettings()
    return ArxivClient(settings)
