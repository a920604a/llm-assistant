from logger import get_logger
from prefect import task
from services.arxiv_client import ArxivClient
from services.metadata_fetcher import MetadataFetcher
from services.pdf_parser import PDFParserService

logger = get_logger(__name__)


@task(retries=2)
async def process_pdfs_task(
    client: ArxivClient, papers: PDFParserService, download_pdfs: bool = True
):
    pdf_parser = PDFParserService()
    metadata_fetcher = MetadataFetcher(client, pdf_parser)  # client 已不需
    pdf_results = await metadata_fetcher.process_pdfs_batch(papers, download_pdfs)

    print(f"Processed PDFs: {pdf_results.get('parsed', 0)} parsed")
    return pdf_results
