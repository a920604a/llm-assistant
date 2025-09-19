import pathlib
import time
from string import Template

from prefect import get_run_logger
from services.langchain_client import llm_html_foramt, llm_summary, llm_translate


def fetch_paper_info(paper: dict, content_map: dict[str, str]) -> dict:
    """整理單篇論文資訊，包含 raw_content（若有）"""

    logger = get_run_logger()

    paper_info = {
        "title": paper.get("title") or "No Title",
        "authors": paper.get("authors") or [],
        "abstract": paper.get("abstract") or "",
        "pdf_url": paper.get("pdf_url") or None,
        "published_date": paper.get("published_date") or None,
    }

    arxiv_id = paper.get("arxiv_id")
    if arxiv_id and arxiv_id in content_map:
        logger.info(
            f"fetch_paper_info arxiv_id = {arxiv_id} found in content_map {paper_info}"
        )
        paper_info["raw_content"] = content_map[arxiv_id]

    else:
        logger.debug(f"fetch_paper_info arxiv_id ={arxiv_id} not found in content_map")

    return paper_info


def trim_summary(summary: str, level: str) -> str:
    """
    根據 summary_level 做摘要裁剪
    - short: 保留「主要發現」「結論」段落
    - detailed: 保留完整內容
    """
    if not summary or not isinstance(summary, str):
        return "Summary not available."

    if level == "short":
        lines = summary.split("\n")
        filtered = [line for line in lines if "主要發現" in line or "結論" in line]
        return "\n".join(filtered) if filtered else summary[:300] + "..."
    return summary


def summarize_paper(paper_info: dict, user: dict, retries: int = 3) -> str:
    """呼叫 LLM 生成摘要，若失敗則 fallback"""
    logger = get_run_logger()
    summary = ""
    while len(summary) < 100 and retries > 0:
        summary = llm_summary(paper=paper_info, user=user, max_words=1000)
        if summary and isinstance(summary, str) and len(summary) >= 100:
            break
        retries -= 1
        logger.info(f"Retrying summary generation, attempts left: {retries}")

        if len(summary) < 100:
            logger.warning(f"Summary seems too short: {summary}")

    return summary


def format_html(
    paper_info: dict,
    idx: int,
    summary: str,
) -> str:
    pdf_url = paper_info.get("pdf_url")
    pdf_link_html = (
        f'<a href="{pdf_url}" target="_blank">Preview PDF</a>' if pdf_url else "N/A"
    )

    summary = llm_html_foramt(summary)

    return f"""
    <div class="paper-summary">
        <div class="paper-title">{idx}. {paper_info["title"]}</div>
        <div class="paper-meta">
            <strong>Authors:</strong> {", ".join(paper_info.get("authors", []))} <br>
            <strong>Published:</strong> {paper_info.get("published_date", "N/A")} <br>
            <strong>PDF:</strong> {pdf_link_html}
        </div>
        <div class="paper-abstract">
            {summary}
        </div>
    </div>
    """


def generate_summary(
    papers_and_content: tuple[list[dict], dict[str, str]], user: dict
) -> str:
    """
    將每篇論文生成 LLM 摘要，並整理成 HTML
    """
    logger = get_run_logger()
    start = time.time()
    papers, content_map = papers_and_content

    if not papers:
        logger.info("No papers to summarize.")
        return "<p>No new papers today.</p>"

    logger.info(f"Generating summary for {len(papers)} papers...")

    papers_html = ""

    for idx, p in enumerate(papers, start=1):
        paper_info = fetch_paper_info(p, content_map)
        # Stage 1: 摘要
        # Stage 2: 翻譯
        # Stage 3: HTML 格式化

        summary = summarize_paper(paper_info, user)
        logger.info(f"summarize_paper {summary}")
        summary = llm_translate(user, summary)

        logger.info(f"llm_translate {summary}")

        logger.info(
            f"[Generate Summary Stage] Summary paper {paper_info['title']} the amount of text is {len(summary)}"
        )

        papers_html += format_html(paper_info, idx, summary)

    template_path = pathlib.Path(__file__).parent / "template.html"
    template_text = template_path.read_text(encoding="utf-8")
    final_html = Template(template_text).substitute(papers_html=papers_html)

    # logger.info("-" * 50)
    # logger.info(papers_html)

    # file_path = "daily_summary.html"

    # with open(file_path, "w", encoding="utf-8") as f:
    #     f.write(final_html)

    logger.info(
        f"[Generate Summary Stage] Summary generation completed in {time.time() - start:.2f}s"
    )
    return final_html
