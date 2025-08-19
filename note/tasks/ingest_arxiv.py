# tasks/ingest_arxiv.py
from celery_app import celery_app
from arxiv_ingestion.flows.arxiv_pipeline import arxiv_pipeline
from datetime import datetime, timedelta

from logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="run_daily_arxiv_pipeline")
def run_daily_pipeline(max_results=10, process_pdfs=True):
    logger.info("🚀 Worker started, triggering  Arxiv pipeline...")
    target_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d")
    arxiv_pipeline(
        target_date=target_date, max_results=max_results, process_pdfs=process_pdfs
    )
