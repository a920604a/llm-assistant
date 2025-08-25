from config import MODEL_NAME, OLLAMA_API_URL
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def llm_context(context: str, query: str, user_language: str = "Traditional Chinese"):
    chat_model = ChatOllama(model=MODEL_NAME, temperature=0.6, base_url=OLLAMA_API_URL)

    prompt = ChatPromptTemplate.from_template(
        """
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
        {"context": context, "question": query, "user_language": user_language}
    )

    return resp.content


if __name__ == "__main__":
    context = "LangChain 是一個用於構建 LLM 應用的框架。"
    query = "什麼是 LangChain？"
    result = llm_context(context, query)
    print(result)
