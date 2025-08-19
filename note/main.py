from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import threading
import asyncio
from datetime import datetime, timedelta
from prometheus_fastapi_instrumentator import Instrumentator
from api.routers import query, user
from arxiv_ingestion.flows.arxiv_pipeline import arxiv_pipeline
from storage.qdrant import create_qdrant_collection as create_note_collection
from arxiv_ingestion.db.qdrant import (
    create_qdrant_collection as create_arxiv_collection,
)
from arxiv_ingestion.db.minio import create_bucket_if_not_exists

from logger import get_logger

logger = get_logger(__name__)


app = FastAPI()
Instrumentator().instrument(app).expose(app)

origins = ["http://mcpclient:8000"]


# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routers

app.include_router(query.router, tags=["query"])
app.include_router(user.router, tags=["user"])


# Startup event: 確保 Qdrant 啟動後再建立 collection
@app.on_event("startup")
async def startup_event():
    create_note_collection()
    create_arxiv_collection()
    create_bucket_if_not_exists()
