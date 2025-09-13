# REST API routers
from api.auto_metrics import observe_api
from api.schemas.user import UserQuery
from api.verify_token import verify_firebase_token  # 解析 Firebase token
from core.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from services.aggregator import generate_stream, process_user_query

router = APIRouter()


@router.post("/api/v1/ask")
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

    try:
        if not query:
            return {"error": "Query 不可為空"}

        result = process_user_query(query, user_id=user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process question: {str(e)}"
        )


@router.post("/api/v1/stream")
@limiter.limit("7/minute")  # 每分鐘 7 次
async def ask_question_stream(
    request: Request,
    user_query: UserQuery,
    user_id: str = Depends(verify_firebase_token),
) -> StreamingResponse:
    """Streaming RAG endpoint - returns answer as it's generated."""

    query = user_query.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query 不可為空")

    return StreamingResponse(
        generate_stream(query, user_id),
        media_type="text/plain",  # 前端 fetch 會逐段讀取
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
