from typing import List

from prefect import get_run_logger, task
from services.common import get_cached_services
from services.schemas import ArxivPaper


@task(retries=3, retry_delay_seconds=10)
async def fetch_papers_task(
    date_from: str, date_to: str, max_results: int = 5
) -> List[ArxivPaper]:
    logger = get_run_logger()
    client = get_cached_services()
    papers = await client.fetch_papers(
        from_date=date_from, to_date=date_to, max_results=max_results
    )
    logger.info(f"Fetched {len(papers)} papers from {date_from} to {date_to}")
    return papers
