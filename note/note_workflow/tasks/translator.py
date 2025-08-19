# tasks/translate.py
from prefect import task
from note_workflow.tasks.llm import llm


@task
def ollama_translate(text: str) -> str:
    prompt = f"請幫我將以下內容翻譯成繁體中文：\n{text}"
    return llm(prompt)
