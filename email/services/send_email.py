# services/send_email_sync.py
import anyio
from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
)


def send_email_sync(
    subject: str,
    recipients: list[str],
    body: str,
    attachments: list[dict] = None,  # [{"filename": "summary.pdf", "content": b"..."}]
):
    async def _send():
        fm = FastMail(conf)
        for r in recipients:
            msg = MessageSchema(
                subject=subject,
                recipients=[r],
                body=body,
                subtype="html",
                # FastMail attachments 需 list of dict [{"filename": ..., "content": bytes, "type": "application/pdf"}]
                attachments=[
                    {
                        "filename": att["filename"],
                        "content": att["content"],
                        "type": "application/pdf",
                    }
                    for att in attachments or []
                ],
            )
            await fm.send_message(msg)  # 直接 await 單封信
            logger.info(f"Email sent to {r}")

    anyio.run(_send)
