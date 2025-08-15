# REST API routers
import requests
import logging
from fastapi import APIRouter
from services.rag import rag
from api.schemas.query import Query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/query")
def ask_host(query: Query):
    q = query.text.strip()
    logger.error("ask_host %s", q)

    return rag(q)
