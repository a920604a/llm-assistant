from storage import db_session
from storage.model import UserSentPaper


def filter_already_sent_papers(user_id: int, papers: list[dict]) -> list[dict]:
    with db_session() as db:
        sent_arxiv_ids = {
            r.arxiv_id
            for r in db.query(UserSentPaper)
            .filter(UserSentPaper.user_id == user_id)
            .all()
        }
    new_papers = [p for p in papers if p["arxiv_id"] not in sent_arxiv_ids]
    return new_papers
