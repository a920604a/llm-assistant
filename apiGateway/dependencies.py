from typing import Annotated

from config import Settings, get_settings
from fastapi import Depends, Request
from services.ollama.client import OllamaClient


def get_ollama_client(request: Request) -> OllamaClient:
    """Get Ollama client from the request state."""
    return request.app.state.ollama_client


SettingsDep = Annotated[Settings, Depends(get_settings)]
OllamaDep = Annotated[OllamaClient, Depends(get_ollama_client)]
