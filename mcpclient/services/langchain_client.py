from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from conf import MODEL_NAME, USER_LANGUAGE, OLLAMA_API_URL


def llm(query: str):
    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

    prompt = ChatPromptTemplate.from_template(
        """
    You are a helpful assistant.
    
    Question:
    {question}

    Answer in {USER_LANGUAGE}, concise and clear.
    """
    )

    chain = prompt | chat_model

    resp = chain.invoke({"question": query, "USER_LANGUAGE": USER_LANGUAGE})

    return resp.content


if __name__ == "__main__":
    query = "什麼是 LangChain？"
    result = llm(query)
    print(result)
