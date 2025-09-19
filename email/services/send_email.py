# services/send_email_sync.py
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings
from logger import AppLogger
from prefect import get_run_logger

logger = AppLogger(__name__).get_logger()


def send_email(
    subject: str,
    recipients: str,
    body: str,
    attachments: list[dict] = None,  # [{"filename": "summary.pdf", "content": bytes}]
):
    """
    使用 smtplib 發送 HTML 郵件 + 附件，保留與原 FastMail 相同的函數接口。
    """
    logger = get_run_logger()
    start = time.time()

    # 建立多部分郵件（HTML + 附件）
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = recipients

    # 加入 HTML 內容
    msg.attach(MIMEText(body, "html"))

    # 加入附件
    for att in attachments or []:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(att["content"])
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f'attachment; filename="{att["filename"]}"'
        )
        msg.attach(part)

    try:
        # 使用 Gmail 或其他 SMTP server
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")

    logger.info(f"[Send Email] cost in {time.time() - start:.2f}s")
