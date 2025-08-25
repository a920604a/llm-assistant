from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from storage.model import Paper


def fetch_new_papers(db: Session, since_date=None, limit: int = 5) -> list[Paper]:
    """
    從 papers table 抓取新論文
    - 條件: pdf_parsed = True 或 published_date >= 昨天
    """
    if since_date is None:
        since_date = datetime.utcnow() - timedelta(days=30)  # 預設抓過去 30 天
    papers = (
        db.query(Paper)
        .filter(Paper.pdf_parsed | (Paper.published_date >= since_date.date()))
        .limit(limit)
        .all()
    )
    return papers
