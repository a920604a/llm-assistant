# REST API routers
import requests
from fastapi import APIRouter
from services.rag import rag

router = APIRouter()




@router.post("api/query")
def ask_host(query: str):
    q = query.strip()
    
    return rag(q)