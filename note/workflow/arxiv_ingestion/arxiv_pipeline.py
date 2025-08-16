import asyncio
import logging
from datetime import datetime, timedelta
from prefect import flow
from tasks.fetch_papers import fetch_papers_task
from tasks.process_pdfs import process_pdfs_task
from tasks.store_papers import store_papers_task
from tasks.generate_report import generate_report_task

from prefect import get_run_logger

@flow(name="Arxiv Paper Pipeline")
def arxiv_pipeline(target_date: str, max_results: int = 10, process_pdfs: bool = True):
    
    logger = get_run_logger()

    client, papers = fetch_papers_task(target_date, max_results)
    
    if process_pdfs and papers:
        pdf_results = process_pdfs_task(client, papers)

        logger.info(f"Stored {len(pdf_results.get('updated_papers', []  ))} papers in DB")


        stored_count = store_papers_task(pdf_results.get("updated_papers", []))
    else:
        pdf_results = {"parsed": 0, "downloaded": 0, "errors": []}

        logger.info(f"Stored {len(papers)} papers in DB")


        stored_count = store_papers_task(papers)
    
    result_summary = {
        "papers_fetched": len(papers),
        "pdfs_downloaded": pdf_results.get("downloaded", 0),
        "pdfs_parsed": pdf_results.get("parsed", 0),
        "papers_stored": stored_count,
        "errors": pdf_results.get("errors", []),
    }

    # 呼叫日報告 task
    report = generate_report_task(result_summary)
    logger.info(f"\n{report}")

    
    
if __name__ == "__main__":
    target_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y%m%d")
    arxiv_pipeline(target_date=target_date, max_results=100, process_pdfs=False)
    
    