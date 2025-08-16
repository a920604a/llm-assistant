from prefect import task
from datetime import datetime

@task
def generate_report_task(result_summary: dict) -> str:
    """
    產生日報告文字 (可擴充成 PDF, Markdown, Email...)
    """
    report_time = datetime.utcnow().isoformat()
    report = (
        f"📄 Arxiv Ingestion Report @ {report_time}\n"
        f"- Papers fetched: {result_summary.get('papers_fetched', 0)}\n"
        f"- PDFs downloaded: {result_summary.get('pdfs_downloaded', 0)}\n"
        f"- PDFs parsed: {result_summary.get('pdfs_parsed', 0)}\n"
        f"- Papers stored: {result_summary.get('papers_stored', 0)}\n"
        f"- Errors: {len(result_summary.get('errors', []))}\n"
    )

    if result_summary.get("errors"):
        report += "  Error details:\n"
        for err in result_summary["errors"][:5]:  # 最多列前 5 個錯誤
            report += f"    - {err}\n"

    return report
