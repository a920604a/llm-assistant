import time

from prefect import get_run_logger
from storage import db_session
from storage.model import UserSentPaper


def record_sent_papers(user_id: int, arxiv_ids: list[str]):
    logger = get_run_logger()
    start = time.time()

    with db_session() as db:
        for arxiv_id in arxiv_ids:
            db.add(UserSentPaper(user_id=user_id, arxiv_id=arxiv_id))
        db.commit()

    logger.info(f"[Record Sent Paper Stage] cost in {time.time() - start:.2f}s")
