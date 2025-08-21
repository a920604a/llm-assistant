# tasks/translate.py
from note_workflow.tasks.llm import llm
from prefect import task


@task
def ollama_translate(text: str) -> str:
    prompt = f"請幫我將以下內容翻譯成繁體中文：\n{text}"
    return llm(prompt)
