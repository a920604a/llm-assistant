from api.schemas.history import ChatMessage
from storage.crud.chat_history import fetch_chat_history


def fetch_chat(user_id: str, limit: int) -> list[ChatMessage]:
    result = []
    chat = fetch_chat_history(user_id=user_id, limit=limit)
    for data in chat:
        result.append(
            ChatMessage(
                id=data["id"],
                role="user",
                content=data["input"],
                timestamp=data["timestamp"],
            )
        )
        result.append(
            ChatMessage(
                id=data["id"],
                role="bot",
                content=data["output"],
                timestamp=data["timestamp"],
            )
        )
    return result
