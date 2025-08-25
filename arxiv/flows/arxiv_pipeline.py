from datetime import datetime, timedelta

from db.minio import create_note_bucket
from db.qdrant import create_qdrant_collection

# from prefect import get_run_logger
from logger import get_logger
from prefect import flow
from tasks.fetch_papers import fetch_papers_task
from tasks.generate_report import generate_report_task
from tasks.process_pdfs import process_pdfs_task
from tasks.qdrant_index import qdrant_index_task
from tasks.store_papers import store_papers_task

logger = get_logger()


@flow(name="Arxiv Paper Ingestion Pipeline")
def arxiv_pipeline(
    date_from: str, date_to: str, max_results: int = 10, download_pdfs: bool = True
):
    # logger = get_run_logger()

    client, papers = fetch_papers_task(date_from, date_to, max_results)

    if papers:
        pdf_results = process_pdfs_task(client, papers, download_pdfs)

        if pdf_results.get("updated_papers"):
            papers = pdf_results["updated_papers"]

    else:
        pdf_results = {"parsed": 0, "downloaded": 0, "errors": []}

    print(f"Stored {len(papers)} papers in DB")

    # 新增：先建立 Qdrant Index
    indexed_count = qdrant_index_task(papers)
    print(f"Qdrant Index {indexed_count}")

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
    print(f"\n{report}")


if __name__ == "__main__":
    create_qdrant_collection()
    create_note_bucket()
    arxiv_pipeline(
        date_from=(datetime.utcnow() - timedelta(days=30)).strftime("%Y%m%d"),
        date_to=datetime.utcnow().strftime("%Y%m%d"),
        max_results=3,
        download_pdfs=False,
    )
