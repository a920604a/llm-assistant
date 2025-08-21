import json
import re
from typing import Dict, List


def llm_text_to_json(llm_text: str) -> List[Dict]:
    """
    將 LLM 回傳的論文文字解析成 JSON。

    範例輸出：
    [
      {
        "title": "Qwen2‑7B Instruct",
        "authors": "Qwen Team",
        "year": 2024,
        "abstract": "介紹 Qwen2‑7B Instruct 模型的架構..."
      },
      ...
    ]

    注意：
    - 如果 LLM 已經可以輸出 JSON，建議直接使用 JSON。
    - 此函式用於解析類似 Markdown/文字格式的輸出。
    """
    # 正則匹配編號、標題、作者、年份、摘要
    pattern = r"\d+\.\s*\*\*(.*?)\*\*\s*–\s*(.*?)\s*\((\d{4})\)\s*\*(.*?)\*"
    papers = []

    for match in re.finditer(pattern, llm_text, re.DOTALL):
        title, authors, year, abstract = match.groups()
        # 簡單容錯
        if not title or not authors or not year or not abstract:
            continue
        papers.append(
            {
                "title": title.strip(),
                "authors": authors.strip(),
                "year": int(year.strip()),
                "abstract": abstract.strip(),
            }
        )

    return papers


# 生成 HTML Email
def generate_email_html(papers_json: List[Dict]) -> str:
    paper_items = ""
    for p in papers_json:
        paper_items += f"<li><strong>{p['title']}</strong> - {p['authors']} ({p['year']})<br>{p['abstract']}</li>\n"

    html = f"""
    <div style='font-family:Arial,sans-serif;line-height:1.5;color:#333;'>
      <h2>📧 您有新的摘要通知</h2>
      <ul>
        {paper_items}
      </ul>
      <p>點擊下方按鈕查看更多細節：</p>
      <a href="https://yourapp.com" style="padding:10px 15px; background:#007bff; color:white; text-decoration:none; border-radius:4px;">查看詳情</a>
      <p style='font-size:12px;color:#888;margin-top:20px;'>© 2025 Your Company. 如不希望收到此類郵件，可<a href="#">取消訂閱</a></p>
    </div>
    """
    return html


# -----------------------------
# 範例使用
if __name__ == "__main__":
    llm_text = """
    **近期值得閱讀的論文（2023‑2024）**
    1. **Qwen2‑7B Instruct** – Qwen Team (2024) *介紹 Qwen2‑7B Instruct 模型的架構、訓練流程與在指令式對話上的表現。*
    2. **StableBeluga‑7B** – Stability AI (2023) *提出 StableBeluga‑7B，結合多模態推理，並在多領域任務上取得新高。*
    """

    papers_json = llm_text_to_json(llm_text)
    print(json.dumps(papers_json, ensure_ascii=False, indent=2))
