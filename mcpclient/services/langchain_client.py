from config import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langfuse import get_client
from logger import get_logger
from services.langfuse_client import LangfuseObs

logger = get_logger(__name__)

langfuse = get_client()


obs = LangfuseObs(mode="callback")  # langchain mode
# obs = LangfuseObs(mode="sdk")  # langchain mode


@obs.observe_fn
def llm(
    query: str,
    isTranslate: bool,
    user_language: str = "English",
    user_id: str = "anonymous",
) -> str:
    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

    # obs.set_user(user_id)
    # obs.set_tags(["translation", "Auth service"])
    # obs.set_metadata({"user_language": user_language})

    if isTranslate:
        # 使用 user_language 指定語言
        prompt_template = """
        You are a helpful assistant.

        Question:
        {question}

        Answer in {user_language}, concise and clear.
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        resp = chain.invoke(
            {"question": query, "user_language": user_language},
            config=obs.get_config(
                user_id=user_id,
                tags=["translation", "Auth service"],
            ),
        )
    else:
        # 不翻譯，使用預設語言
        prompt_template = """
        You are a helpful assistant.

        Question:
        {question}

        Answer concise and clear.
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        resp = chain.invoke(
            {"question": query},
            config=obs.get_config(
                user_id=user_id,
                tags=["Not translation", "Auth service"],
            ),
        )

    return resp.content


def rewrite_query(query: str, user_id: str) -> str:
    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

    prompt_template = """
    You are a professional query rewriting assistant.

    Original Question:
    {question}

    Rewrite the question clearly and concisely for information retrieval.
    Only output the rewritten query, do not answer it.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | chat_model
    resp = chain.invoke(
        {"question": query},
        config=obs.get_config(
            user_id=user_id,
            tags=["rewrite_query", "Auth service"],
        ),
    )

    return resp.content


if __name__ == "__main__":
    q = "什麼是 LangChain？"

    # 使用翻譯
    result = llm(
        q, isTranslate=True, user_language="Traditional Chinese", user_id="test_user"
    )
    logger.info(result)

    # 不翻譯
    result2 = llm(q, isTranslate=False, user_id="test_user")
    logger.info(result2)
