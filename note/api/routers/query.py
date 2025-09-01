# REST API routers
from api.schemas.query import Query
from fastapi import APIRouter
from logger import AppLogger
from storage.redis_client import get_redis_system_setting

logger = AppLogger(__name__).get_logger()

router = APIRouter()


@router.post("/api/query")
def ask_host(query: Query):
    q = query.text.strip()
    logger.info("ask_host %s", q)
    from arxiv_ingestion.flows.arxiv_rag_pipeline import rag  # <- lazy import

    system_settings = get_redis_system_setting(query.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_host %s, top_k=%s, user_language=%s", q, top, lang)

    llm_reply = rag(query=q, system_settings=system_settings, user_id=query.user_id)
    return llm_reply
