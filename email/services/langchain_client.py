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
    paper: dict 含 title, authors, abstract
    """
    if not paper:
        return "No paper provided."

    title = paper.get("title", "No Title")
    authors = ", ".join(paper.get("authors", []))
    abstract = paper.get("abstract", "")

    chat_model = ChatOllama(
        model=MODEL_NAME, temperature=temperature, base_url=OLLAMA_API_URL
    )

    # 安全生成 prompt
    prompt_lines = [
        "You are a professional research assistant.",
        f"Summarize the following paper concisely, in no more than {max_words} words.",
        "Keep it readable for an email newsletter.",
    ]
    if isTranslate:
        # 明確要求只輸出翻譯後文本，不保留原文
        prompt_lines.append(
            f"Translate the summary to {user_language}. Output ONLY in {user_language}."
        )

    prompt_lines.append(
        "Paper:\nTitle: {title}\nAuthors: {authors}\nAbstract: {abstract}"
    )

    prompt_template = "\n".join(prompt_lines)

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | chat_model

    input_vars = {"title": title, "authors": authors, "abstract": abstract}
    if isTranslate:
        input_vars["user_language"] = user_language

    resp = chain.invoke(input_vars)

    return resp.content.strip()
