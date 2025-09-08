import io
from datetime import datetime

from config import settings
from prefect import get_run_logger
from services.langchain_client import llm_summary
from storage.minio import s3_client


def format_paper_html(paper: dict, summary: str) -> str:
    """格式化單篇論文的 HTML 區塊"""
    authors_str = ", ".join(paper.get("authors") or [])

    # 防呆：避免 None / 空值
    safe_title = paper.get("title") or "No Title"
    safe_summary = summary or "Summary not available."
    pdf_url = paper.get("pdf_url")

    # title 當作連結
    if pdf_url:
        title_html = f'<h3><a href="{pdf_url}" target="_blank">{safe_title}</a></h3>'
    else:
        title_html = f"<h3>{safe_title}</h3>"

    return f"""
    <li>
        {title_html}
        <p><em>{authors_str}</em></p>
        <div>
            <strong>Summary:</strong>
            <p>{safe_summary}</p>
        </div>
    </li>
    """


def fetch_paper_info(paper: dict, content_map: dict[str, str]) -> dict:
    """整理單篇論文資訊，包含 raw_content（若有）"""
    paper_info = {
        "title": paper.get("title") or "No Title",
        "authors": paper.get("authors") or [],
        "abstract": paper.get("abstract") or "",
        "pdf_url": paper.get("pdf_url") or None,
    }

    arxiv_id = paper.get("arxiv_id")
    if arxiv_id and arxiv_id in content_map:
        paper_info["raw_content"] = content_map[arxiv_id]

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


def summarize_paper(paper_info: dict, user: dict, logger) -> str:
    """呼叫 LLM 生成摘要，若失敗則 fallback"""
    try:
        summary = llm_summary(paper_info, user)
        if not summary or not isinstance(summary, str):
            return "No summary available."
        # 根據 user["summary_level"] 決定輸出
        level = user.get("summary_level", "detailed")
        return trim_summary(summary, level)
    except Exception as e:
        logger.error(f"Failed to generate summary for '{paper_info['title']}': {e}")
        return "Summary generation failed."


def save_summary_to_s3(html: str, arxiv_id: str) -> str:
    """
    將 HTML 上傳到 S3 / MinIO
    :param html: 生成的 HTML 內容
    :param s3_client: boto3.client("s3") 物件
    :param bucket: S3 / MinIO bucket 名稱
    :param object_name: 存到 S3 的路徑/檔名 (例如 "summaries/daily_paper_summary.html")
    :return: S3 物件名稱
    """
    logger = get_run_logger()

    today_str = datetime.today().strftime("%Y-%m-%d")
    object_name = f"{arxiv_id}/summary_{today_str}.html"

    try:
        buffer = io.BytesIO(html.encode("utf-8"))
        s3_client.upload_fileobj(
            buffer,
            settings.MINIO_NOTE_BUCKET,
            object_name,
            ExtraArgs={
                "ContentType": "text/html",  # ✅ 讓瀏覽器知道是 HTML
                "ContentDisposition": "inline",  # ✅ inline = 預覽, attachment = 強制下載
                "CacheControl": "max-age=3600",  # （可選）瀏覽器快取
            },
        )
        logger.info(f"Uploaded summary to s3://{object_name}")
        return object_name
    except Exception as e:
        logger.error(f"Failed to upload summary to S3: {e}")
        raise


def generate_summary(
    papers_and_content: tuple[list[dict], dict[str, str]], user: dict
) -> str:
    """
    將每篇論文生成 LLM 摘要，並整理成 HTML，附上 PDF 連結
    """
    papers, content_map = papers_and_content
    logger = get_run_logger()

    if not papers:
        logger.info("No papers to summarize.")
        return "<p>No new papers today.</p>"

    logger.info(f"Generating summary for {len(papers)} papers...")
    htmls = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.5; }
            .paper-summary { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; background-color: #f9f9f9; }
            .paper-title { font-size: 1.2em; font-weight: bold; margin-bottom: 5px; }
            .paper-meta { font-size: 0.9em; color: #555; margin-bottom: 10px; }
            .paper-summary:nth-child(even) { background-color: #f1f1f1; }
        </style>
    </head>
    <body>
        <h2>今日論文摘要</h2>
    """

    for idx, p in enumerate(papers, start=1):
        paper_info = fetch_paper_info(p, content_map)
        summary = summarize_paper(paper_info, user, logger)

        pdf_url = paper_info.get("pdf_url")
        pdf_link_html = (
            f'<a href="{pdf_url}" target="_blank">Download PDF</a>'
            if pdf_url
            else "N/A"
        )

        html = f"""
        <div class="paper-summary">
            <div class="paper-title">{idx}. {paper_info["title"]}</div>
            <div class="paper-meta">
                Authors: {", ".join(paper_info.get("authors", []))} <br>
                Published: {paper_info.get("published_date", "N/A")} <br>
                PDF: {pdf_link_html}
            </div>
            <p>{summary}</p>
        </div>
        """
        htmls += html

    htmls += """
    <p><em>本摘要僅供參考，最終請依原始論文與專業判斷。</em></p>
    </body>
    </html>
    """

    logger.info("Summary generation completed.")
    return htmls
