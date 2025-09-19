from prefect import get_run_logger, task
from services.common import get_cached_services
from services.metadata_fetcher import MetadataFetcher
from services.pdf_parser import PDFParserService


@task(retries=2)
async def process_pdfs_task(papers: PDFParserService, store_to_db: bool):
    logger = get_run_logger()
    client = get_cached_services()
    pdf_parser = PDFParserService(max_pages=20, max_file_size_mb=10)
    metadata_fetcher = MetadataFetcher(client, pdf_parser)

    pdf_results = await metadata_fetcher.process_pdfs_batch(papers)

    logger.info(f"Processed PDFs: {pdf_results.get('parsed', 0)} parsed ")

    if store_to_db:
        stored_count = metadata_fetcher.store_to_db(
            papers, pdf_results.get("parsed_papers", {})
        )

        pdf_results["papers_stored"] = stored_count
    else:
        pdf_results["papers_stored"] = 0
        pdf_results["papers_indexed"] = 0

    return pdf_results
