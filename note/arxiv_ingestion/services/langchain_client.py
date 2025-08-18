from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from arxiv_ingestion.config import MODEL_NAME, USER_LANGUAGE, OLLAMA_API_URL


def llm_context(context: str, query: str):

    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

    prompt = ChatPromptTemplate.from_template(
        """
    You are a note organizer. Please organize your answers based on the following:

    Context:
    {context}

    Question:
    {question}

    Answer in {USER_LANGUAGE}, list format.
    """
    )

    chain = prompt | chat_model

    resp = chain.invoke(
        {"context": context, "question": query, "USER_LANGUAGE": USER_LANGUAGE}
    )

    return resp.content


if __name__ == "__main__":
    context = "LangChain 是一個用於構建 LLM 應用的框架。"
    query = "什麼是 LangChain？"
    result = llm_context(context, query)
    print(result)
