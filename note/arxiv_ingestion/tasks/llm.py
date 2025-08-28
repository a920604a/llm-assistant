from prefect import task
from services.langchain_client import llm_context


@task
def llm(
    context: str,
    prompt: str,
    user_language: str = "Traditional Chinese",
    user_id: str = "anonymous",
    system_prompt: str = "",
) -> str:
    return llm_context(
        context,
        prompt,
        user_language=user_language,
        user_id=user_id,
        system_prompt=system_prompt,
    )
