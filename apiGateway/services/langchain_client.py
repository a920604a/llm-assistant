from api.schemas.SystemSetting import SystemSettings
from config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langfuse import get_client
from logger import AppLogger
from services.langfuse_client import LangfuseObs

logger = AppLogger(__name__).get_logger()

langfuse = get_client()


obs = LangfuseObs(mode="callback")  # langchain mode
# obs = LangfuseObs(mode="sdk")  # langchain mode


@obs.observe_fn
def llm(
    query: str,
    system_setting: SystemSettings,
    user_id: str = "anonymous",
) -> str:
    temperature = system_setting.temperature
    isTranslate = system_setting.translate
    user_language = system_setting.user_language
    system_prompt = system_setting.system_prompt

    chat_model = ChatOllama(
        model=settings.MODEL_NAME,
        temperature=temperature,
        base_url=settings.OLLAMA_API_URL,
    )

    # obs.set_user(user_id)
    # obs.set_tags(["translation", "Auth service"])
    # obs.set_metadata({"user_language": user_language})

    if isTranslate:
        # 使用 user_language 指定語言
        prompt_template = """
        {system_prompt}
        You are a helpful assistant.

        Question:
        {question}

        Answer in {user_language}, concise and clear.
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        resp = chain.invoke(
            {
                "system_prompt": system_prompt,
                "question": query,
                "user_language": user_language,
            },
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
            {"system_prompt": system_prompt, "question": query},
            config=obs.get_config(
                user_id=user_id,
                tags=["Not translation", "Auth service"],
            ),
        )

    return resp


@obs.observe_fn
def rewrite_query(query: str, user_id: str) -> str:
    chat_model = ChatOllama(
        model=settings.MODEL_NAME,
        temperature=0.2,
        base_url=settings.OLLAMA_API_URL,
    )

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
    q = "What is LangChain？"

    cache = {
        "user_language": "zh",
        "translate": True,
        "system_prompt": "",
        "top_k": 5,
        "use_rag": True,
        "subscribe_email": False,
        "reranker_enabled": True,
        "temperature": 0.7,
    }
    # 使用翻譯
    result = llm(q, cache, user_id="test_user")
    logger.info(result.content)

    cache["translate"] = False

    # 不翻譯
    result2 = llm(q, cache, user_id="test_user")
    logger.info(result2.content)

    # async def main():
    #     query = "什麼是 LangChain？"
    #     cache = {
    #         "temperature": 0.7,
    #         "system_prompt": "You are a helpful assistant.",
    #         "translate": True,  # 是否翻譯
    #         "user_language": "zh",  # 翻譯成的語言
    #     }

    #     async for chunk in llm_stream(query, cache, user_id="test_user"):
    #         # chunk 是模型生成的部分文字
    #         logger.info(chunk)  # 或 print(chunk, end="") 邊輸出邊顯示

    # asyncio.run(main())
