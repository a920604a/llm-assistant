import time

from prefect import get_run_logger, task
from storage import db_session
from storage.model import UserSentPaper


@task(name="Filter Already Sent Paper")
def filter_already_sent_papers(user_id: int, papers: list[dict]) -> list[dict]:
    logger = get_run_logger()
    start = time.time()
    with db_session() as db:
        sent_arxiv_ids = {
            r.arxiv_id
            for r in db.query(UserSentPaper)
            .filter(UserSentPaper.user_id == user_id)
            .all()
        }
    new_papers = [p for p in papers if p["arxiv_id"] not in sent_arxiv_ids]
    logger.info(
        f"[Filter Already Sent Paper Stage] {len(new_papers)} paper then in {time.time() - start:.2f}s"
    )
    return new_papers
