import logging
from prefect import task

from arxiv_ingestion.services.metadata_fetcher import MetadataFetcher

logger = logging.getLogger(__name__)


@task
def store_papers_task(papers):
    metadata_fetcher = MetadataFetcher(None, None)
    stored_count = metadata_fetcher.store_to_db(papers)
    logger.info(f"Stored {stored_count} papers in DB")
    return stored_count
