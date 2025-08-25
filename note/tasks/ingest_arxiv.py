# tasks/ingest_arxiv.py
from datetime import datetime, timedelta

from arxiv_ingestion.flows.arxiv_pipeline import arxiv_pipeline
from celery_app import celery_app
from logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="run_daily_arxiv_pipeline", queue="notes")
def run_daily_pipeline(max_results=10, process_pdfs=True):
    logger.info("🚀 Worker started, triggering  Arxiv pipeline...")
    arxiv_pipeline(
        date_from=(datetime.utcnow() - timedelta(days=30)).strftime("%Y%m%d"),
        date_to=datetime.utcnow().strftime("%Y%m%d"),
        max_results=max_results,
        download_pdfs=process_pdfs,
    )
