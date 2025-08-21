from conf import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def llm(query: str, isTranslate: bool, user_language: str = "English") -> str:
    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

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
        resp = chain.invoke({"question": query, "user_language": user_language})
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
        resp = chain.invoke({"question": query})

    return resp.content


def rewrite_query(query):
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
    resp = chain.invoke({"question": query})

    return resp.content


if __name__ == "__main__":
    query = "什麼是 LangChain？"

    # 使用翻譯
    result = llm(query, isTranslate=True, user_language="Traditional Chinese")
    print(result)

    # 不翻譯
    result2 = llm(query, isTranslate=False)
    print(result2)
