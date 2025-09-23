from typing import Annotated

from config import Settings, get_settings
from fastapi import Depends, Request
from services.langchain.client import LangChainClient
from services.langfuse.client import LangfuseTracer
from services.ollama.client import OllamaClient


def get_ollama_client(request: Request) -> OllamaClient:
    """Get Ollama client from the request state."""
    return request.app.state.ollama_client


def get_langchain_client(request: Request) -> LangChainClient:
    """Get LangChain client from the request state."""
    return request.app.state.langchain_client


def get_langfuse_tracer(request: Request) -> LangfuseTracer:
    """Get Langfuse tracer from the request state."""
    return request.app.state.langfuse_tracer


SettingsDep = Annotated[Settings, Depends(get_settings)]
OllamaDep = Annotated[OllamaClient, Depends(get_ollama_client)]
LangChainDep = Annotated[LangChainClient, Depends(get_langchain_client)]
LangfuseDep = Annotated[LangfuseTracer, Depends(get_langfuse_tracer)]
