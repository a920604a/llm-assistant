# REST API routers
import requests
from fastapi import APIRouter, Depends

from api.schemas.user import UserQuery
from services.aggregator import process_user_query
from api.verify_token import verify_firebase_token  # 解析 Firebase token

router = APIRouter()


@router.post("/api/ask")
def ask_host(user_query: UserQuery, user_id: str = Depends(verify_firebase_token)):
    """
    Host API 入口：
    1. 接收使用者 query
    2. 呼叫 Ollama LLM 處理（可做初步理解與規劃）
    3. 呼叫指定的 MCP Server 處理子任務（此例為 Note Service）
    4. 將結果回傳前端
    """
    query = user_query.query.strip()

    if not query:
        return {"error": "Query 不可為空"}

    result = process_user_query(user_query, user_id=user_id)
    return {"reply": result}
