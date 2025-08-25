from arxiv_ingestion.services.metadata_fetcher import MetadataFetcher
from logger import get_logger
from prefect import task

logger = get_logger(__name__)


@task
def store_papers_task(papers):
    metadata_fetcher = MetadataFetcher(None, None)
    stored_count = metadata_fetcher.store_to_db(papers)
    print(f"Stored {stored_count} papers in DB")
    return stored_count
