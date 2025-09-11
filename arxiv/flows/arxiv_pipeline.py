import asyncio
from datetime import datetime, timedelta

from db.minio import create_note_bucket
from db.qdrant import create_qdrant_collection
from logger import AppLogger
from tasks.fetch_papers import fetch_papers_task
from tasks.generate_report import generate_report_task
from tasks.process_pdfs import process_pdfs_task
from tasks.qdrant_index import qdrant_index_task

logger = AppLogger(__name__).get_logger()


def arxiv_pipeline(
    date_from: str, date_to: str, max_results: int = 10, store_to_db: bool = True
):
    results = {
        "papers_fetched": 0,
        "pdfs_downloaded": 0,
        "pdfs_parsed": 0,
        "papers_stored": 0,
        "papers_indexed": 0,
        "errors": [],
        "processing_time": 0,
    }
    logger.info("results")
    start_time = datetime.now()

    # Step 1: Fetch paper metadata from arXiv
    papers = asyncio.run(fetch_papers_task(date_from, date_to, max_results))

    logger.info("fetch_papers_task")
    results["papers_fetched"] = len(papers)

    # Step 2: Process PDFs if requested
    pdf_results = {}
    if papers:
        pdf_results = asyncio.run(process_pdfs_task(papers, store_to_db=True))
        results["pdfs_downloaded"] = pdf_results["downloaded"]
        results["pdfs_parsed"] = pdf_results["parsed"]
        results["errors"].extend(pdf_results["errors"])
        results["papers_stored"] = pdf_results["papers_stored"]
    print(f"Stored {pdf_results['papers_stored']} papers in DB")

    # Step 3: Qdrant Index
    indexed_count, _ = qdrant_index_task(papers, pdf_results.get("parsed_papers", {}))
    results["papers_indexed"] = indexed_count
    print(f"Qdrant Index {indexed_count}")

    # Calculate total processing time
    processing_time = (datetime.now() - start_time).total_seconds()
    results["processing_time"] = processing_time

    result_summary = {
        "papers_fetched": len(papers),
        "pdfs_downloaded": pdf_results.get("downloaded", 0),
        "pdfs_parsed": pdf_results.get("parsed", 0),
        "papers_indexed": indexed_count,
        "papers_stored": pdf_results["papers_stored"],
        "errors": pdf_results.get("errors", []),
    }

    # 呼叫日報告 task
    report = generate_report_task(result_summary)
    print(f"\n{report}")


if __name__ == "__main__":
    create_qdrant_collection()
    create_note_bucket()
    arxiv_pipeline(
        date_from=(datetime.utcnow() - timedelta(days=30)).strftime("%Y%m%d"),
        date_to=datetime.utcnow().strftime("%Y%m%d"),
        max_results=1,
    )
