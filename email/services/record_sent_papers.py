from storage import db_session
from storage.model import UserSentPaper


def record_sent_papers(user_id: int, arxiv_ids: list[str]):
    with db_session() as db:
        for arxiv_id in arxiv_ids:
            db.add(UserSentPaper(user_id=user_id, arxiv_id=arxiv_id))
        db.commit()
