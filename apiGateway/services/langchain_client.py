from api.schemas.SystemSetting import SystemSettings
from config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


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
            }
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
        resp = chain.invoke({"system_prompt": system_prompt, "question": query})

    return resp


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
    resp = chain.invoke({"question": query})

    return resp.content


if __name__ == "__main__":
    q = "What is LangChain？"
    print(q)

    cache = SystemSettings(
        user_language="zh",
        translate=False,
        system_prompt="you are a student",
        top_k=5,
        use_rag=True,
        subscribe_email=False,
        reranker_enabled=True,
        temperature=0.6,  # Default temperature for LLM responses
    )

    # 使用翻譯
    result = llm(q, cache, user_id="test_user")
    logger.info(result.content)

    cache.translate = True

    # 不翻譯
    result2 = llm(q, cache, user_id="test_user")
    logger.info(result2.content)
