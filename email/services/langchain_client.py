from typing import Dict

from config import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def llm_summary(
    paper: Dict,
    isTranslate: bool = False,
    user_language: str = "English",
    temperature: float = 0.5,
    max_words: int = 300,
) -> str:
    """
    將單篇論文生成 concise summary，最多 max_words 字。
    paper: dict 含 title, authors, abstract, (optional) raw_content
    """
    if not paper:
        return "No paper provided."

    title = paper.get("title", "No Title")
    authors = ", ".join(paper.get("authors", []))

    # 優先使用 raw_content，否則 fallback 到 abstract
    content = paper.get("raw_content") or paper.get("abstract", "")
    content_type = "Full Content" if paper.get("raw_content") else "Abstract"

    chat_model = ChatOllama(
        model=MODEL_NAME, temperature=temperature, base_url=OLLAMA_API_URL
    )

    # Prompt 組裝
    prompt_lines = [
        "You are a professional research assistant.",
        f"Summarize the following paper concisely, in no more than {max_words} words.",
        "Keep it readable for an email newsletter.",
        f"(Note: the text provided is the paper's {content_type})",
    ]
    if isTranslate:
        prompt_lines.append(
            f"Translate the summary to {user_language}. Output ONLY in {user_language}."
        )

    prompt_lines.append(
        "Paper:\nTitle: {title}\nAuthors: {authors}\nContent: {content}"
    )

    prompt_template = "\n".join(prompt_lines)
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | chat_model

    input_vars = {
        "title": title,
        "authors": authors,
        "content": content,
    }
    if isTranslate:
        input_vars["user_language"] = user_language

    resp = chain.invoke(input_vars)

    return resp.content.strip()
