# REST API routers
from fastapi import APIRouter

from api.schemas.query import Query
from logger import get_logger
from storage.redis_client import redis_client


logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/query")
def ask_host(query: Query):
    q = query.text.strip()
    logger.info("ask_host %s", q)
    from arxiv_ingestion.flows.arxiv_rag_pipeline import rag  # <- lazy import

    top = redis_client.get(f"{query.user_id}-top_k")
    lang = redis_client.get(f"{query.user_id}-user_language")
    return rag(query=q, top_k=top, user_language=lang)
