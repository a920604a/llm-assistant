# REST API routers
from api.auto_metrics import observe_api
from api.schemas.user import UserQuery
from api.verify_token import verify_firebase_token  # 解析 Firebase token
from core.limiter import limiter
from fastapi import APIRouter, Depends, Request
from services.aggregator import process_user_query

router = APIRouter()


@router.post("/api/ask")
@limiter.limit("7/minute")  # 每分鐘 7 次
@observe_api
def ask_host(
    request: Request,
    user_query: UserQuery,
    user_id: str = Depends(verify_firebase_token),
):
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
