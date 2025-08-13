# REST API routers
import requests
from fastapi import APIRouter
from services.rag import rag
from api.schemas.query import Query

router = APIRouter()


@router.post("/api/query")
def ask_host(query: Query):
    q = query.text.strip()

    return rag(q)
