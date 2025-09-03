from api.auto_metrics import observe_api
from api.schemas.history import ChatMessage
from fastapi import APIRouter
from services.fetch_chat import fetch_chat

router = APIRouter()


@router.get("/api/chat_history", response_model=list[ChatMessage])
@observe_api
async def get_chat_history(user_id: str, limit=5):
    # TODO: 根據 user_id 過濾資料
    return fetch_chat(user_id, limit)
