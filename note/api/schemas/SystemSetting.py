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


DEFAULT_SETTINGS = SystemSettings(
    user_language="Traditional Chinese",
    translate=False,
    system_prompt="",
    top_k=5,
    use_rag=True,
    subscribe_email=False,
    reranker_enabled=True,
)


class PostSettingsRequest(BaseModel):
    user_id: str
    new_settings: SystemSettings
