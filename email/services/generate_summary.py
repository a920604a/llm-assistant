from typing import List

from prefect import get_run_logger
from services.langchain_client import llm_summary


def generate_summary(
    papers: List[dict], translate: bool = False, user_language: str = "English"
) -> str:
    """
    將每篇論文生成 LLM 摘要，並整理成 HTML，附上 PDF 連結
    """
    logger = get_run_logger()
    if not papers:
        logger.info("No papers to summarize.")
        return "<p>No new papers today.</p>"

    html = "<ul>"  # 初始化 HTML 字串
    logger.info(f"Generating summary for {len(papers)} papers...")

    for idx, p in enumerate(papers, start=1):
        paper_info = {
            "title": p["title"] or "No Title",
            "authors": p["authors"] or [],
            "abstract": p["abstract"] or "",
        }

        logger.info(
            f"[{idx}/{len(papers)}] Summarizing paper: {paper_info['title']} and {p['pdf_url']}"
        )
        logger.info(f"translate {translate} and user language {user_language} ")

        # TODO: from qdrant fetch paper's raw content

        try:
            paper_summary = llm_summary(
                paper_info, isTranslate=translate, user_language=user_language
            )
        except Exception as e:
            logger.error(f"Failed to generate summary for '{paper_info['title']}': {e}")
            paper_summary = "Summary generation failed."

        authors_str = ", ".join(p["authors"] or [])
        pdf_link = (
            f'<a href="{p.get("pdf_url")}">PDF is here</a>' if p.get("pdf_url") else ""
        )

        html += f"""
        <li>
            <strong>{paper_info["title"]}</strong> by {authors_str} {pdf_link}<br>
            <p><strong>Summary:</strong> {paper_summary}</p>
        </li>
        """

    html += "</ul>"
    logger.info("Summary generation completed.")

    return html
