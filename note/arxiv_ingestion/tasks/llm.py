from prefect import task
from arxiv_ingestion.services.langchain_client import llm_context


@task
def llm(context: str, prompt: str) -> str:
    return llm_context(context, prompt)
