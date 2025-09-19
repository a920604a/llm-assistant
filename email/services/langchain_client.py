import pathlib
from typing import Dict

from config import MODEL_NAME, OLLAMA_API_URL
from langchain_ollama import ChatOllama

PROMPT_FILE = pathlib.Path(__file__).parent / "prompt_template.txt"


def llm_summary(paper: Dict, user: dict, max_words: int = 300) -> str:
    if not paper:
        return "No paper provided."

    temperature = min(0.2, user.get("temperature", 0.5))

    title = paper.get("title", "No Title")
    authors = ", ".join(paper.get("authors") or [])
    authors_str = ", ".join([a.replace("{", "{{").replace("}", "}}") for a in authors])

    content = paper.get("raw_content") or paper.get("abstract", "")
    content_type = "Full Content" if paper.get("raw_content") else "Abstract"

    # 讀取 prompt template
    template_text = PROMPT_FILE.read_text(encoding="utf-8")

    # GPT-OSS 上限大約是 8192 tokens
    # Prompt 固定部分 = 250
    # Title + Authors = 40

    MAX_CONTENT_TOKENS = 6000  # 算出的最大 tokens
    AVG_TOKEN_LEN = 4.5  # 每 token 平均字元數
    max_content_chars = int(MAX_CONTENT_TOKENS * AVG_TOKEN_LEN)

    content = content[:max_content_chars]

    prompt_template = template_text.format(
        max_words=max_words,
        content_type=content_type,
        title=title,
        authors=authors_str,
        content=content,
    )

    chat_model = ChatOllama(
        model=MODEL_NAME,
        temperature=temperature,
        base_url=OLLAMA_API_URL,
        request_kwargs={"timeout": 300},  # timeout 秒數
        reset_context=True,  # ⚡每次都清掉 session
    )

    try:
        resp = chat_model.invoke(prompt_template)
        summary = resp.content.strip()
        summary = "\n".join([line for line in summary.splitlines() if line.strip()])
        return summary
    except Exception as e:
        return f"<p><strong>Summary generation failed:</strong> {e}</p>"


def llm_translate(user: dict, summary: str) -> str:
    is_translate = user.get("translate", False)
    if not is_translate:
        return summary

    user_language = user.get("user_language", "English")
    temperature = min(0.2, user.get("temperature", 0.5))

    translation_instruction = (
        f"SUMMARIZE AND TRANSLATE THE FOLLOWING PAPER INTO {user_language.upper()} ONLY. "
        "Do NOT output English under any circumstances.",
        summary,
    )

    chat_model = ChatOllama(
        model=MODEL_NAME,
        temperature=temperature,
        base_url=OLLAMA_API_URL,
        request_kwargs={"timeout": 300},  # timeout 秒數
        reset_context=True,  # ⚡每次都清掉 session
    )
    try:
        resp = chat_model.invoke(translation_instruction)
        trans_summary = resp.content.strip()
        trans_summary = "\n".join(
            [line for line in trans_summary.splitlines() if line.strip()]
        )
        return trans_summary
    except Exception as e:
        return f"Summary generation failed:</strong> {e}>"


def llm_html_foramt(summary: str) -> str:
    if not summary or not isinstance(summary, str):
        return "Summary not available."

    chat_model = ChatOllama(
        model=MODEL_NAME,
        temperature=0.0,
        base_url=OLLAMA_API_URL,
        request_kwargs={"timeout": 300},  # timeout 秒數
        reset_context=True,  # ⚡每次都清掉 session
    )

    html_instruction = (
        "Please convert the following summary into a well-structured HTML format suitable for email newsletters. "
        "Use appropriate HTML tags such as <p>, <strong>, <em>, and <ul>/<li> for lists. "
        "Ensure the HTML is clean and free of any unnecessary tags or attributes. "
        "Do not include any CSS or JavaScript. Only provide the HTML content.",
        summary,
    )

    try:
        resp = chat_model.invoke(html_instruction)
        html_summary = resp.content.strip()
        return html_summary
    except Exception as e:
        return f"<p><strong>HTML formatting failed:</strong> {e}</p>"
