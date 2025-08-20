from prefect import task
from services.langchain_client import llm_context


@task
def llm(context: str, prompt: str, user_language: str = "Traditional Chinese") -> str:
    return llm_context(context, prompt, user_language=user_language)
