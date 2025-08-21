from celery import Celery
from celery.schedules import crontab
from celery_prometheus import add_prometheus_option  # 新增導入
from conf import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks.ingest_arxiv"],  # 新增 pipeline task
)
# 確保 Celery Worker 發送事件
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
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
        "args": (2, True),  # 傳入 task 的參數 (max_results=10, process_pdfs=True)
    }
}
