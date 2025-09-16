from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session
from storage.model import Paper
from storage.storage_metrics import monitored_db


@monitored_db
def fetch_new_papers(db: Session, since_date=None, limit: int = 500) -> list[Paper]:
    """
    從 papers table 抓取新論文
    - 條件: pdf_processed = True 或 published_date >= 昨天
    """
    if since_date is None:
        since_date = datetime.utcnow() - timedelta(days=30)  # 預設抓過去 30 天
    papers = (
        db.query(Paper)
        .filter(and_(Paper.pdf_processed, Paper.published_date >= since_date.date()))
        .limit(limit)
        .all()
    )
    return papers
