# REST API routers
import requests
import logging
from fastapi import APIRouter

from arxiv_ingestion.flows.arxiv_rag_pipeline import rag
from api.schemas.query import Query
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/query")
def ask_host(query: Query):
    q = query.text.strip()
    logger.info("ask_host %s", q)

    return rag(q)
