from typing import List

import yagmail
from config import settings
from jinja2 import Environment, FileSystemLoader

# 讀取模板
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("daily_summary.html")


def send_email_sync(
    subject: str, recipients: List[str], papers: list[dict], summary_htmls: str = None
):
    """
    使用 Jinja2 渲染 HTML，並透過 yagmail 發送郵件
    papers: list of dict，包含 title, authors, pdf_url
    summary_htmls: 如果有 LLM summary，則直接插入模板
    """
    # Render HTML
    html_content = template.render(papers=papers, summary_htmls=summary_htmls)

    # 建立 yagmail client
    yag = yagmail.SMTP(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)

    # 發送給每個收件人
    for email in recipients:
        yag.send(to=email, subject=subject, contents=html_content)
