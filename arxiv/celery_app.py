from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready
from celery_prometheus import add_prometheus_option  # 新增導入
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from db.minio import create_note_bucket
from db.qdrant import create_qdrant_collection as create_arxiv_collection
from logger import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "ingest_arxiv",
    broker=CELERY_BROKER_URL,  # 任務的 訊息代理，通常是 Redis 或 RabbitMQ。
    backend=CELERY_RESULT_BACKEND,  # 存放任務的 執行結果 (如 Redis、DB、S3)。
    include=["run_daily_task"],  # 啟動時要自動 import 的任務模組清單
)
celery_app.conf.timezone = "Asia/Taipei"  # 設定時區為 UTC+8
celery_app.conf.enable_utc = False  # 直接用當地時間


# 確保 Celery Worker 發送事件
celery_app.conf.update(
    worker_send_task_events=True,  # 讓 Worker 在執行時發送事件 (開始、完成、失敗)。
    task_send_sent_event=True,  # 在任務 被送到 Queue 時 就發送事件。
)

# 添加 Prometheus 選項
add_prometheus_option(celery_app)


# ----------------------
# Celery Beat 排程
# ----------------------
celery_app.conf.beat_schedule = {
    "daily-arxiv-pipeline": {
        "task": "run_daily_arxiv_pipeline",
        "schedule": crontab(hour=18, minute=30),  # for production
        # "schedule": crontab(minute="*/2"),  # for test
        # "schedule": crontab(minute=15),  # 或者每天每小時第 15 分鐘
        "args": (3, False),  # 傳入 task 的參數 (max_results=10, process_pdfs=True)
    }
}


@worker_ready.connect
def at_start(sender, **kwargs):
    if sender.hostname.startswith("worker.ingest_arxiv@"):
        create_note_bucket()
        logger.info("✅ note_bucket ready")
        create_arxiv_collection()
        logger.info("✅ arxiv_collection ready")
