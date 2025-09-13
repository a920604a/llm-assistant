from typing import Annotated

from config import Settings, get_settings
from fastapi import Depends, Request
from services.cache.client import CacheClient
from services.langchain.client import LangChainClient
from services.minio.client import MinioClient
from services.ollama.client import OllamaClient
from services.qdrant.client import QdrantClient


def get_ollama_client(request: Request) -> OllamaClient:
    """Get Ollama client from the request state."""
    return request.app.state.ollama_client


def get_langchain_client(request: Request) -> LangChainClient:
    """Get langchain client from the request state."""
    return request.app.state.langchain_client


def get_user_cache_client(request: Request) -> CacheClient | None:
    """Get cache client from the request state."""
    return getattr(request.app.state, "cache_user_client", None)


def get_paper_cache_client(request: Request) -> CacheClient | None:
    """Get cache client from the request state."""
    return getattr(request.app.state, "cache_paper_client", None)


def get_qdrant_client(request: Request) -> QdrantClient:
    """Get OpenSearch client from the request state."""
    return request.app.state.qdrant_client


def get_minio_client(request: Request) -> MinioClient:
    """Get OpenSearch client from the request state."""
    return request.app.state.minio_client


# Dependency annotations
QdrantDep = Annotated[QdrantClient, Depends(get_qdrant_client)]
MinioDep = Annotated[MinioClient, Depends(get_minio_client)]

SettingsDep = Annotated[Settings, Depends(get_settings)]
OllamaDep = Annotated[OllamaClient, Depends(get_ollama_client)]
LangchainDep = Annotated[LangChainClient, Depends(get_langchain_client)]

UserCacheDep = Annotated[CacheClient | None, Depends(get_user_cache_client)]
PaperCacheDep = Annotated[CacheClient | None, Depends(get_paper_cache_client)]
