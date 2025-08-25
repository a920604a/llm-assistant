import time
from datetime import datetime, timedelta

from prefect import flow, get_run_logger, task
from services.fetch_new_papers import fetch_new_papers
from services.fetch_paper_content import fetch_paper_content_from_qdrant
from services.generate_summary import generate_summary
from services.get_subscribed_users import get_subscribed_users
from services.send_email import send_email_sync
from storage import db_session

# ----------------------
# Tasks with Observability
# ----------------------


@task(name="Fetch Papers")
def fetch_papers_task(days: int = 1, limit: int = 5) -> list[dict]:
    logger = get_run_logger()

    start = time.time()
    with db_session() as db:
        papers = fetch_new_papers(
            db, since_date=datetime.utcnow() - timedelta(days=days), limit=limit
        )
        # 轉成 dict list
        papers_data = [
            {
                "title": p.title or "No Title",
                "authors": p.authors or [],
                "abstract": p.abstract or "",
                "pdf_url": getattr(p, "pdf_url", None),
                "arxiv_id": getattr(p, "arxiv_id", None),
            }
            for p in papers
        ]
    logger.info(f"Fetched {len(papers_data)} papers in {time.time() - start:.2f}s")
    return papers_data


@task(name="Fetch Paper Content")
def fetch_paper_content(papers: list[dict]) -> dict[str, str]:
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
            f"Abstract: {p['abstract'][:200] + '...' if p['abstract'] else 'N/A'}, "
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
        f"Fetched raw content for {len(content_map)} / {len(papers)} papers in {time.time() - start:.2f}s"
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
    logger.info(f"Found {len(users)} users in {time.time() - start:.2f}s")
    return users


@task(name="Generate Summary")
def generate_summary_task(
    papers: tuple[list[dict], dict[str, str]],
    translate: bool = False,
    user_language: str = "English",
):
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
def daily_papers_flow(top_k: int = 3):
    logger = get_run_logger()

    start_flow = time.time()
    logger.info("Daily papers flow started")

    # Fetch all subscribed user emails, user_id, translate, and user_language
    users = get_users_task()
    papers = fetch_papers_task(days=30, limit=top_k)
    logger.info(f" papers data {papers}")
    if len(papers) == 0:
        logger.info("No new papers found, skipping email sending")
        return

    papers_content_map = fetch_paper_content(papers)
    logger.info(f"Fetched content for {papers_content_map} ")

    # 對每個 user 建立個人化流程
    send_tasks = []
    for u in users:
        email = u.get("email")
        if not email:
            logger.warning(f"User {u.get('user_id')} has no email, skipping")
            continue

        # 個人化 summary task
        summary = generate_summary_task(
            (papers, papers_content_map),
            u.get("translate", False),
            u.get("user_language", "English"),
        )
        send_task = send_email_task("Daily Paper Summary", [email], summary)
        send_tasks.append(send_task)

    # 等待所有發信完成
    for t in send_tasks:
        if t is not None:
            t.result()  # 只有 t 不為 None 才呼叫

    logger.info(f"Daily papers flow completed in {time.time() - start_flow:.2f}s")


if __name__ == "__main__":
    daily_papers_flow(top_k=3)
