import random
import time
from datetime import datetime, timedelta

import firebase_admin
from config import FIREBASE_KEY_PATH
from prefect import flow, get_run_logger, task
from services.fetch_new_papers import fetch_new_papers
from services.fetch_paper_content import fetch_paper_content_from_qdrant
from services.filter_already_sent_papers import filter_already_sent_papers
from services.generate_summary import generate_summary
from services.get_subscribed_users import get_subscribed_users
from services.record_sent_papers import record_sent_papers
from services.send_email import send_email
from storage import db_session

# ----------------------
# Tasks with Observability
# ----------------------


@task(name="Fetch Papers")
def fetch_papers_task(days: int = 5) -> list[dict]:
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
                "arxiv_id": getattr(p, "arxiv_id", None),
                "published_date": getattr(p, "published_date", None),
            }
            for p in papers
        ]
    logger.info(
        f"Fetched papers published_date >= {datetime.utcnow() - timedelta(days=days)}"
    )
    logger.info(
        f"[Fetch Papers Stage] Fetched {len(papers_data)} papers in {time.time() - start:.2f}s"
    )
    return papers_data


@task(name="Fetch Paper Content")
def fetch_paper_content_task(papers: list[dict]) -> dict[str, str]:
    """
    從 Qdrant 裡抓取每篇 paper 的 raw_content，
    回傳 {arxiv_id: raw_content} dict
    """
    logger = get_run_logger()
    start = time.time()

    logger.info(f"Fetching paper content for {len(papers)} papers from Qdrant")

    content_map = {}

    for p in papers:
        logger.info(
            f"Paper {p['arxiv_id']}: "
            f"Title: {p['title'] or 'No Title'}, "
            f"Authors: {', '.join(p['authors']) if p['authors'] else 'N/A'}, "
            f"Abstract: {p['abstract'][:50] + '...' if p['abstract'] else 'N/A'}, "
            f"PDF URL: {p['pdf_url']}"
        )
        logger.debug(f"Paper data: {p}")

        arxiv_id = p.get("arxiv_id")
        # if not arxiv_id:
        #     continue  # 沒有 arxiv_id 的略過

        raw_content = fetch_paper_content_from_qdrant(
            arxiv_id=arxiv_id,
            title=p.get("title"),
        )
        if raw_content:
            content_map[arxiv_id] = raw_content
            logger.info(
                f"Fetched raw content for {len(raw_content)} for {arxiv_id} papers"
            )

    logger.info(
        f"[Fetch Paper Content Stage] Fetched raw content for {len(content_map)} / {len(papers)} papers in {time.time() - start:.2f}s"
    )
    return content_map


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
    logger.info(
        f"[Get Subscribed Users Stage] Found {len(users)} users in {time.time() - start:.2f}s"
    )
    return users


# ----------------------
# Per-User Task 封裝流程
# ----------------------


@task(name="Process User Task", retries=3, retry_delay_seconds=5)
def process_user_task(user: dict, papers: list[dict], content_map: dict):
    """
    - user: dict, 包含 user_id, email, translate, user_language
    - papers: list[dict] 今天分配給這個 user 的論文
    - content_map: dict[arxiv_id, raw_content]
    """
    logger = get_run_logger()
    user_id = user.get("user_id")
    email = user.get("email")
    logger.info(f"[Process User Task Stage] user : {user_id} got {len(papers)} paper")

    if not email:
        logger.warning(f"User {user_id} has no email, skipping")
        return {"user_id": user_id, "status": "skipped", "reason": "no email"}

    if not papers:
        logger.info(f"No papers assigned to user {user_id}, skipping")
        return {"user_id": user_id, "status": "skipped", "reason": "no papers"}

    # 生成 summary
    try:
        summary_html = generate_summary((papers, content_map), user)
    except Exception as e:
        logger.error(
            f"[Process User Task Stage] Failed to generate summary for user {user_id}: {e}"
        )
        return {"user_id": user_id, "status": "failed", "reason": f"summary error: {e}"}

    # 發送 email
    try:
        send_email(
            subject="Daily Paper Summary",
            recipients=email,
            body=summary_html,
        )
        logger.info(f"[User {user_id}] Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        return {"user_id": user_id, "status": "failed", "reason": f"email error: {e}"}

    # 記錄已寄送
    arxiv_ids = [p["arxiv_id"] for p in papers if p.get("arxiv_id")]
    record_sent_papers(user_id, arxiv_ids)

    logger.info(f"Sent {len(papers)} papers to user {user_id} ({email})")
    return {"user_id": user_id, "status": "success", "sent_count": len(papers)}


# ----------------------
# Flow
# ----------------------


@flow(name="Daily Subscribe Flow")
def daily_papers_flow(top_k: int = 3):
    # 初始化 Firebase
    cred = firebase_admin.credentials.Certificate(
        f"{FIREBASE_KEY_PATH}/serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred)

    logger = get_run_logger()

    start_flow = time.time()
    logger.info("Daily Subscribe Flow started")

    # Fetch all subscribed user emails, user_id, translate, and user_language
    users = get_users_task()
    if not users:
        logger.info("No subscribed users found, skipping flow")
        return
    papers = fetch_papers_task()
    if not papers:
        logger.info("No new papers found, skipping flow")
        return

    content_map = fetch_paper_content_task(papers)
    if not content_map:
        logger.info("No paper content found, skipping flow")
        return

    for user in users:
        user_unsent_papers = filter_already_sent_papers(
            user["user_id"], papers
        )  # 返回 dict list
        logger.info(f"user {user['user_id']}")
        logger.info(f"user_unsent_papers   {len(user_unsent_papers)}")
        if not user_unsent_papers:
            logger.info(f"user {user['user_id']} - All papers have been sent, skipping")
            continue

        # 打亂順序
        random.shuffle(user_unsent_papers)

        # 取 top_k
        assigned_papers = user_unsent_papers[:top_k]
        logger.info(f"got top_k {top_k} paper, sorest paper {len(assigned_papers)}")
        # 發送給使用者
        result = process_user_task(user, assigned_papers, content_map)
        logger.info(result)

    logger.info(f"Daily Subscribe Flow completed in {time.time() - start_flow:.2f}s")


if __name__ == "__main__":
    # import firebase_admin
    # from config import FIREBASE_KEY_PATH

    # # 初始化 Firebase
    # cred = firebase_admin.credentials.Certificate(
    #     f"{FIREBASE_KEY_PATH}/serviceAccountKey.json"
    # )
    # firebase_admin.initialize_app(cred)

    daily_papers_flow(top_k=2)
