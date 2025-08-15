from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import logging
import sys
from prometheus_fastapi_instrumentator import Instrumentator
from api.routers import query, user, upload

from storage.qdrant import create_qdrant_collection


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
app.include_router(upload.router, tags=["upload"])


# Startup event: 確保 Qdrant 啟動後再建立 collection
# Startup event: 確保 Qdrant 啟動後再建立 collection
@app.on_event("startup")
async def startup_event():
    logger.info("Waiting for Qdrant to be ready...")
    max_retry = 10

    for i in range(max_retry):
        try:
            create_qdrant_collection()  # 內部已處理「已存在」情況
            logger.info("✅ Qdrant collection is ready.")
            break
        except Exception as e:
            logger.warning(f"Qdrant not ready yet ({i+1}/{max_retry}): {e}")
            time.sleep(3)
    else:
        logger.error("❌ Failed to ensure Qdrant collection after multiple retries.")
