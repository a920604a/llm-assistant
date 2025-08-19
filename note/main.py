from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import threading
from datetime import datetime, timedelta
from prometheus_fastapi_instrumentator import Instrumentator
from api.routers import query, user, upload
from storage.qdrant import create_qdrant_collection
from arxiv_ingestion.flows.arxiv_pipeline import arxiv_pipeline
from arxiv_ingestion.db.qdrant import create_qdrant_collection
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
app.include_router(upload.router, tags=["upload"])


# ---------------------- Background daily pipeline ----------------------
def daily_pipeline_runner():
    """每天執行 Arxiv pipeline，不阻塞 API"""
    while True:
        target_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d")
        try:
            logger.info("🔹 Running daily Arxiv pipeline...")
            arxiv_pipeline(target_date=target_date, max_results=5, process_pdfs=True)
            logger.info("✅ Pipeline run completed.")
        except Exception as e:
            logger.exception(f"❌ Pipeline failed: {e}")

        # 等一天再跑
        time.sleep(24 * 60 * 60)


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

    # 🔹 啟動時先跑一次 pipeline
    create_qdrant_collection()
    create_bucket_if_not_exists()
    try:
        target_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d")
        logger.info("🔹 Running initial Arxiv pipeline at startup...")
        arxiv_pipeline(target_date=target_date, max_results=10, process_pdfs=True)
        logger.info("✅ Initial pipeline run completed.")
    except Exception as e:
        logger.exception(f"❌ Initial pipeline failed: {e}")

    # 啟動每天 pipeline 的 background thread
    threading.Thread(target=daily_pipeline_runner, daemon=True).start()
    logger.info("🔹 Daily Arxiv pipeline runner started in background.")
