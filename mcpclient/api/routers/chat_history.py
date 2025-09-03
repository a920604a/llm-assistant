from datetime import datetime

from api.auto_metrics import observe_api
from api.schemas.history import ChatMessage
from api.verify_token import verify_firebase_token
from fastapi import APIRouter, Depends
from logger import AppLogger
from services.fetch_chat_history import fetch_chat

logger = AppLogger(__name__).get_logger()


router = APIRouter()

fake_db = [
    ChatMessage(
        id="1",
        role="user",
        content="What is RAG?",
        timestamp=datetime(2025, 9, 3, 9, 0),
    ),
    ChatMessage(
        id="2",
        role="bot",
        content="RAG stands for Retrieval-Augmented Generation...",
        timestamp=datetime(2025, 9, 3, 9, 0, 5),
    ),
]


@router.get("/api/chat/history", response_model=list[ChatMessage])
@observe_api
async def get_chat_history(user_id: str = Depends(verify_firebase_token), limit=5):
    logger.info(f"Fetching chat history for user {user_id}")
    # TODO: 根據 user_id 過濾資料
    return fetch_chat(user_id, limit)
