from typing import List, Tuple

from arxiv_ingestion.config import ArxivSettings
from arxiv_ingestion.services.arxiv_client import ArxivClient
from arxiv_ingestion.services.schemas import ArxivPaper
from logger import get_logger
from prefect import task

logger = get_logger(__name__)


@task(retries=3, retry_delay_seconds=10)
async def fetch_papers_task(
    date_from: str, date_to: str, max_results: int = 5
) -> Tuple[ArxivClient, List[ArxivPaper]]:
    settings = ArxivSettings()
    client = ArxivClient(settings)
    papers = await client.fetch_papers(
        from_date=date_from, to_date=date_to, max_results=max_results
    )
    print(f"Fetched {len(papers)} papers from {date_from} to {date_to}")
    return client, papers
