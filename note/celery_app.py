from celery import Celery
from celery.schedules import crontab
from celery_prometheus import add_prometheus_option  # 新增導入
from conf import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "ingest_arxiv",
    broker=CELERY_BROKER_URL,  # 任務的 訊息代理，通常是 Redis 或 RabbitMQ。
    backend=CELERY_RESULT_BACKEND,  # 存放任務的 執行結果 (如 Redis、DB、S3)。
    include=["tasks.ingest_arxiv"],  # 啟動時要自動 import 的任務模組清單
)

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
        # "schedule": crontab(hour=0, minute=0), # for production
        "schedule": crontab(minute="*/5"),  # for test
        # "schedule": crontab(minute=15),  # 或者每天每小時第 15 分鐘
        "args": (3, True),  # 傳入 task 的參數 (max_results=10, process_pdfs=True)
    }
}
