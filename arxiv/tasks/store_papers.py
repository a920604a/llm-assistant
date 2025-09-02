from logger import AppLogger
from prefect import task
from services.metadata_fetcher import MetadataFetcher

logger = AppLogger(__name__).get_logger()


@task
def store_papers_task(papers):
    metadata_fetcher = MetadataFetcher(None, None)
    stored_count = metadata_fetcher.store_to_db(papers)
    print(f"Stored {stored_count} papers in DB")
    return stored_count
