from prefect import flow
from tasks.environment import setup_environment_task
from tasks.fetch import fetch_daily_papers_task
from tasks.pdf_retry import process_failed_pdfs_task
from tasks.opensearch import create_opensearch_placeholders_task
from tasks.report import generate_daily_report_task
from tasks.cleanup import cleanup_temp_files_task

@flow(name="arxiv_paper_ingestion", log_prints=True)
def daily_arxiv_flow(target_date: str = None):
    # 1. Setup
    setup_result = setup_environment_task()
    
    # 2. Fetch papers
    fetch_results = fetch_daily_papers_task(target_date=target_date)
    
    # 3. Retry failed PDFs
    retry_results = process_failed_pdfs_task(fetch_results=fetch_results)
    
    # 4. Create OpenSearch placeholders
    opensearch_results = create_opensearch_placeholders_task(fetch_results=fetch_results)
    
    # 5. Generate daily report
    report = generate_daily_report_task(
        fetch_results=fetch_results,
        retry_results=retry_results,
        opensearch_results=opensearch_results,
    )
    
    # 6. Cleanup
    cleanup_temp_files_task()
    
    return report

if __name__ == "__main__":
    daily_arxiv_flow()
