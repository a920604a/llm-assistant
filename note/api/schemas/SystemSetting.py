from pydantic import BaseModel
from typing import Optional


class SystemSettings(BaseModel):
    user_language: str
    translate: bool
    system_prompt: str
    top_k: int
    use_rag: bool
    subscribe_email: bool
    reranker_enabled: bool
    temperature: float = 0.6  # LLM temperature, default to 0.6


DEFAULT_SETTINGS = SystemSettings(
    user_language="Traditional Chinese",
    translate=False,
    system_prompt="",
    top_k=5,
    use_rag=True,
    subscribe_email=False,
    reranker_enabled=True,
    temperature=0.6,  # Default temperature for LLM responses
)


class PostSettingsRequest(BaseModel):
    user_id: str
    new_settings: SystemSettings
