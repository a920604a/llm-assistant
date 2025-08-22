import time
from datetime import datetime, timedelta

from prefect import flow, get_run_logger, task
from services.fetch_new_papers import fetch_new_papers
from services.generate_summary import generate_summary
from services.get_subscribed_users import get_subscribed_users
from services.send_email import send_email_sync
from storage import db_session

# ----------------------
# Tasks with Observability
# ----------------------


@task(name="Fetch Papers")
def fetch_papers_task(days: int = 1):
    logger = get_run_logger()

    start = time.time()
    with db_session() as db:
        papers = fetch_new_papers(
            db, since_date=datetime.utcnow() - timedelta(days=days)
        )
        # 轉成 dict list
        papers_data = [
            {
                "title": p.title or "No Title",
                "authors": p.authors or [],
                "abstract": p.abstract or "",
                "pdf_url": getattr(p, "pdf_url", None),
            }
            for p in papers
        ]
    logger.info(f"Fetched {len(papers_data)} papers in {time.time() - start:.2f}s")
    return papers_data


@task(name="Get Subscribed Users")
def get_users_task():
    logger = get_run_logger()

    start = time.time()
    logger.info("Fetching subscribed users")
    with db_session() as db:
        users = get_subscribed_users(db)
        # [{
        #         "user_id": user.id,
        #         "email": email,
        #         "translate": setting.translate,
        #         "user_language": setting.user_language,
        #     }]
    logger.info(f"Found {len(users)} users in {time.time() - start:.2f}s")
    return users


@task(name="Generate Summary")
def generate_summary_task(papers, translate=False, user_language="English"):
    logger = get_run_logger()

    start = time.time()
    logger.info("Generating summary")
    summary = generate_summary(papers, translate=translate, user_language=user_language)
    logger.info(f"Summary generated in {time.time() - start:.2f}s")
    return summary


@task(name="Send Email", retries=3, retry_delay_seconds=5)
def send_email_task(subject: str, recipients: list[str], body: str):
    logger = get_run_logger()
    try:
        send_email_sync(subject, recipients, body)
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        raise e


# ----------------------
# Flow
# ----------------------


@flow(name="Daily Papers Flow")
def daily_papers_flow():
    logger = get_run_logger()

    start_flow = time.time()
    logger.info("Daily papers flow started")

    # Fetch all subscribed user emails, user_id, translate, and user_language
    users = get_users_task()
    papers = fetch_papers_task(days=30)
    if len(papers) == 0:
        logger.info("No new papers found, skipping email sending")
        return
    # 對每個 user 建立個人化流程
    send_tasks = []
    for u in users:
        email = u.get("email")
        if not email:
            logger.warning(f"User {u.get('user_id')} has no email, skipping")
            continue
        # 個人化 summary task
        summary = generate_summary_task(
            papers, u.get("translate", False), u.get("user_language", "English")
        )
        send_task = send_email_task("Daily Paper Summary", [email], summary)
        send_tasks.append(send_task)

    # 等待所有發信完成
    for t in send_tasks:
        if t is not None:
            t.result()  # 只有 t 不為 None 才呼叫

    logger.info(f"Daily papers flow completed in {time.time() - start_flow:.2f}s")
