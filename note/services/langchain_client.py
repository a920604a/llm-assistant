from config import settings
from langchain_core.messages.ai import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from services.langfuse_client import LangfuseObs

obs = LangfuseObs(mode="callback")  # langchain mode


def llm_context(
    context: str,
    query: str,
    user_language: str = "Traditional Chinese",
    temperature: float = 0.5,
    system_prompt: str = "",
    user_id: str = "anonymous",
) -> AIMessage:
    chat_model = ChatOllama(
        model=settings.MODEL_NAME,
        temperature=temperature,
        base_url=settings.OLLAMA_API_URL,
    )

    prompt = ChatPromptTemplate.from_template(
        """
    {system_prompt}
    You are an expert note organizer and Markdown formatter.
    Please read the following context and question, and provide a well-structured answer
    using headings, subheadings, bullet points, and numbering where appropriate.


    Context:
    {context}

    Question:
    {question}

    Translate the summary to {user_language}. Output ONLY in {user_language}, formatted clearly for readability with headings, bullet points, and numbering.
    """
    )

    chain = prompt | chat_model

    resp = chain.invoke(
        {
            "system_prompt": system_prompt,
            "context": context,
            "question": query,
            "user_language": user_language,
        },
        config=obs.get_config(
            user_id=user_id,
            tags=["llm_context", "note services"],
        ),
    )

    return resp


def rewrite_query(query: str, user_id: str) -> str:
    chat_model = ChatOllama(
        model=settings.MODEL_NAME, temperature=0.6, base_url=settings.OLLAMA_API_URL
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
            tags=["rewrite_query", "note service"],
        ),
    )

    return resp.content


if __name__ == "__main__":
    context = "LangChain 是一個用於構建 LLM 應用的框架。"
    query = "什麼是 LangChain？"
    result = llm_context(
        context, query, temperature=0.6, system_prompt="請用繁體中文回答。"
    )
    print(result)
