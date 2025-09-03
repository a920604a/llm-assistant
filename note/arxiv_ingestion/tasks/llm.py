from langchain_core.messages.ai import AIMessage
from prefect import task
from services.langchain_client import llm_context, rewrite_query


@task
def llm(
    context: str,
    prompt: str,
    user_language: str = "Traditional Chinese",
    user_id: str = "anonymous",
    system_prompt: str = "",
) -> AIMessage:
    return llm_context(
        context,
        prompt,
        user_language=user_language,
        user_id=user_id,
        system_prompt=system_prompt,
    )


@task
def rewrite(query: str, user_id: str) -> str:
    return rewrite_query(query, user_id)
