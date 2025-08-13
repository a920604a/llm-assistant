from celery import Celery
from celery_prometheus import add_prometheus_option  # 新增導入




celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["tasks.upload"]
)
# 確保 Celery Worker 發送事件
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 添加 Prometheus 選項
add_prometheus_option(celery_app)