# REST API routers
from api.auto_metrics import observe_api
from api.schemas.ask import AskRequest, AskResponse
from api.schemas.query import Query
from arxiv_ingestion.flows.arxiv_rag_pipeline import rag, rag_stream
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from logger import AppLogger
from storage.redis_client import get_redis_system_setting

logger = AppLogger(__name__).get_logger()

router = APIRouter()

ask_router = APIRouter(tags=["ask"])
stream_router = APIRouter(tags=["stream"])


@ask_router.post("/api/v1/ask", response_model=AskResponse)
@observe_api
def ask_host(query: AskRequest) -> AskResponse:
    q = query.text.strip()
    logger.info("ask_host %s", q)

    system_settings = get_redis_system_setting(query.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_host %s, top_k=%s, user_language=%s", q, top, lang)

    llm_reply = rag(query=q, system_settings=system_settings, user_id=query.user_id)

    return llm_reply


@stream_router.post("/api/v1/stream")
async def ask_question_stream(query: Query):
    q = query.text.strip()
    logger.info("ask_host %s", q)

    system_settings = get_redis_system_setting(query.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_host %s, top_k=%s, user_language=%s", q, top, lang)

    return StreamingResponse(
        rag_stream(q, system_settings=system_settings, user_id=query.user_id),
        media_type="text/plain",  # 前端 fetch 會逐段讀取
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
