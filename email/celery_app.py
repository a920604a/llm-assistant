import firebase_admin
from celery import Celery
from celery.schedules import crontab
from celery_prometheus import add_prometheus_option  # 新增導入
from config import FIREBASE_KEY_PATH, settings
from firebase_admin import credentials

# 初始化 Firebase
cred = credentials.Certificate(f"{FIREBASE_KEY_PATH}/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


celery_app = Celery(
    "email_service",
    broker=settings.REDIS_BROKER,
    backend=settings.REDIS_BACKEND,
    include=["email_alarm_task"],  # 新增 pipeline task
)


# 確保 Celery Worker 發送事件
celery_app.conf.update(
    worker_send_task_events=True,  # 讓 Worker 在執行時發送事件 (開始、完成、失敗)。
    task_send_sent_event=True,  # 在任務 被送到 Queue 時 就發送事件。
)


# 添加 Prometheus 選項
add_prometheus_option(celery_app)


celery_app.conf.beat_schedule = {
    "daily_paper_summary": {
        "task": "send_daily_papers",
        "schedule": crontab(hour=8, minute=0),  # 每天 8:00 AM
        # "schedule": crontab(minute=15),  # 或者每天每小時第 15 分鐘
        # "schedule": crontab(minute="*/2"),  # for test
    },
}
