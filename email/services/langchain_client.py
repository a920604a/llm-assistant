import pathlib
from typing import Dict

from config import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

PROMPT_FILE = pathlib.Path(__file__).parent / "prompt_template.txt"


def llm_summary(paper: Dict, user: dict, max_words: int = 300) -> str:
    if not paper:
        return "No paper provided."

    is_translate = user.get("translate", False)
    user_language = user.get("user_language", "English")
    temperature = user.get("temperature", 0.5)
    system_prompt = user.get("system_prompt", "")

    title = paper.get("title", "No Title")
    authors = ", ".join(paper.get("authors") or [])
    content = paper.get("raw_content") or paper.get("abstract", "")
    content_type = "Full Content" if paper.get("raw_content") else "Abstract"

    translation_instruction = ""
    if is_translate:
        translation_instruction = (
            f"Translate the summary to {user_language}. Output ONLY in {user_language}."
        )

    # 讀取 prompt template
    template_text = PROMPT_FILE.read_text(encoding="utf-8")

    prompt_template = template_text.format(
        system_prompt=system_prompt,
        max_words=max_words,
        content_type=content_type,
        translation_instruction=translation_instruction,
        title=title,
        authors=authors,
        content=content,
    )

    chat_model = ChatOllama(
        model=MODEL_NAME,
        temperature=temperature,
        base_url=OLLAMA_API_URL,
    )

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | chat_model

    try:
        resp = chain.invoke({})
        html_summary = resp.content.strip()
        html_summary = "\n".join(
            [line for line in html_summary.splitlines() if line.strip()]
        )
        return html_summary
    except Exception as e:
        return f"<p><strong>Summary generation failed:</strong> {e}</p>"
