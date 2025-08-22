# services/send_email_sync.py
import anyio
from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from logger import get_logger

logger = get_logger("send_email_sync")

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
)


def send_email_sync(subject: str, recipients: list[str], body: str):
    async def _send():
        fm = FastMail(conf)
        for r in recipients:
            msg = MessageSchema(
                subject=subject, recipients=[r], body=body, subtype="html"
            )
            await fm.send_message(msg)  # 直接 await 單封信
            logger.info(f"Email sent to {r}")

    anyio.run(_send)
