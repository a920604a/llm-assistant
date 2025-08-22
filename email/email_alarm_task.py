from celery_app import celery_app
from config import settings
from fastapi_mail import ConnectionConfig
from pipeline import daily_papers_flow

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
)


@celery_app.task(name="send_daily_papers", queue="email")
def send_daily_papers():
    daily_papers_flow()
