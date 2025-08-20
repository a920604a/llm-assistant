from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from api.routers import query, user, setting
from starlette.concurrency import run_in_threadpool

from storage.qdrant import create_qdrant_collection as create_note_collection
from arxiv_ingestion.db.qdrant import (
    create_qdrant_collection as create_arxiv_collection,
)

from storage.minio import create_note_bucket

from logger import get_logger

logger = get_logger(__name__)


app = FastAPI(title="Note Server")
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
app.include_router(setting.router, tags=["setting"])


# Startup event: 確保 Qdrant 啟動後再建立 collection
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 startup_event triggered")
    await run_in_threadpool(create_note_collection)
    logger.info("✅ note_collection ready")
    await run_in_threadpool(create_arxiv_collection)
    logger.info("✅ arxiv_collection ready")
    await run_in_threadpool(create_note_bucket)
    logger.info("✅ note_bucket ready")
