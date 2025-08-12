# REST API routers
import requests
from fastapi import APIRouter

from api.schemas.user import UserQuery
from services.aggregator import process_user_query

router = APIRouter()


# === MCP Client 範例（用 requests 模擬） ===
def call_mcp_server(server_url: str, payload: dict):
    resp = requests.post(server_url, json=payload)
    return resp.json()


@router.post("/ask")
def ask_host(user: UserQuery):
    """
    Host API 入口：
    1. 接收使用者 query
    2. 呼叫 Ollama LLM 處理（可做初步理解與規劃）
    3. 呼叫指定的 MCP Server 處理子任務（此例為 Note Service）
    4. 將結果回傳前端
    """
    query = user.query.strip()

    if not query:
        return {"error": "Query 不可為空"}
    
    
    result = process_user_query(query)
    return result
