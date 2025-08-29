from typing import Dict

from config import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from services.langfuse_client import LangfuseObs

obs = LangfuseObs(mode="callback")  # langchain mode


def llm_summary(
    paper: Dict,
    user: dict,
    max_words: int = 300,
) -> str:
    """
    將單篇論文生成 concise summary，最多 max_words 字。
    paper: dict 含 title, authors, abstract, (optional) raw_content
    """
    if not paper:
        return "No paper provided."

    isTranslate = user.get("translate", False)
    user_language = user.get("user_language", "English")
    temperature = user.get("temperature", 0.5)
    system_prompt = user.get("system_prompt", "")

    title = paper.get("title", "No Title")
    authors = ", ".join(paper.get("authors", []))

    # 優先使用 raw_content，否則 fallback 到 abstract
    content = paper.get("raw_content") or paper.get("abstract", "")
    content_type = "Full Content" if paper.get("raw_content") else "Abstract"

    chat_model = ChatOllama(
        model=MODEL_NAME,
        temperature=temperature,
        base_url=OLLAMA_API_URL,
    )

    # Prompt 組裝
    prompt_lines = [
        system_prompt,
        "You are a professional research assistant.",
        f"Summarize the following paper concisely, in no more than {max_words} words.",
        "Keep it readable for an email newsletter.",
        f"(Note: the text provided is the paper's {content_type})",
    ]
    if isTranslate:
        prompt_lines.append(
            f"Translate the summary to {user_language}. Output ONLY in {user_language}, formatted clearly for readability with headings, bullet points, and numbering."
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

    resp = chain.invoke(
        input_vars,
        config=obs.get_config(
            user_id=user.get("user_id", "anonymous"),
            tags=["llm_summary", "email services"],
        ),
    )

    return resp.content.strip()
