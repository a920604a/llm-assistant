from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)
celery_app.conf.task_routes = {
    "services.upload_tasks.import_md_notes_task": {"queue": "notes"}
}
