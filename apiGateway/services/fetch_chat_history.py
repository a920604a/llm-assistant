import requests
from api.schemas.history import ChatMessage
from config import settings


def fetch_chat(user_id: str, limit=10) -> list[ChatMessage]:
    resp = requests.get(
        f"{settings.NOTE_API_URL}/api/chat_history",
        params={"user_id": user_id, "limit": limit},
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()
