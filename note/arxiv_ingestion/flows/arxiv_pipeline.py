from datetime import datetime, timedelta

from arxiv_ingestion.db.minio import create_note_bucket
from arxiv_ingestion.db.qdrant import create_qdrant_collection
from arxiv_ingestion.tasks.fetch_papers import fetch_papers_task
from arxiv_ingestion.tasks.generate_report import generate_report_task
from arxiv_ingestion.tasks.process_pdfs import process_pdfs_task
from arxiv_ingestion.tasks.qdrant_index import qdrant_index_task
from arxiv_ingestion.tasks.store_papers import store_papers_task

# from prefect import get_run_logger
from logger import get_logger
from prefect import flow

logger = get_logger()


@flow(name="Arxiv Paper Ingestion Pipeline")
def arxiv_pipeline(target_date: str, max_results: int = 10, process_pdfs: bool = True):
    # logger = get_run_logger()

    client, papers = fetch_papers_task(target_date, max_results)

    if process_pdfs and papers:
        pdf_results = process_pdfs_task(client, papers)

        if pdf_results.get("updated_papers"):
            papers = pdf_results["updated_papers"]

    else:
        pdf_results = {"parsed": 0, "downloaded": 0, "errors": []}

    logger.info(f"Stored {len(papers)} papers in DB")

    # 新增：先建立 Qdrant Index
    indexed_count = qdrant_index_task(papers)
    logger.info(f"Qdrant Index {indexed_count}")

    stored_count = store_papers_task(papers)

    result_summary = {
        "papers_fetched": len(papers),
        "pdfs_downloaded": pdf_results.get("downloaded", 0),
        "pdfs_parsed": pdf_results.get("parsed", 0),
        "papers_indexed": indexed_count,
        "papers_stored": stored_count,
        "errors": pdf_results.get("errors", []),
    }

    # 呼叫日報告 task
    report = generate_report_task(result_summary)
    logger.info(f"\n{report}")


if __name__ == "__main__":
    create_qdrant_collection()
    create_note_bucket()

    target_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d")
    arxiv_pipeline(target_date=target_date, max_results=1, process_pdfs=True)
