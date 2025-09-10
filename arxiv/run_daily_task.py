# tasks/ingest_arxiv.py
from datetime import datetime, timedelta

from celery_app import celery_app
from flows.arxiv_pipeline import arxiv_pipeline
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


@celery_app.task(name="run_daily_arxiv_pipeline", queue="notes")
def run_daily_pipeline(max_results=10):
    logger.info("🚀 Worker started, triggering  Arxiv pipeline...")
    arxiv_pipeline(
        # date_from=(datetime.utcnow() - timedelta(days=30)).strftime("%Y%m%d"),
        date_from=(datetime.utcnow() - timedelta(days=1)).strftime(
            "%Y%m%d"
        ),  #  production
        date_to=datetime.utcnow().strftime("%Y%m%d"),
        max_results=max_results,
    )
