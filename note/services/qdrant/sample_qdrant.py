import asyncio
import os

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from qdrant_client import models as model_qdrant
from sentence_transformers import SentenceTransformer
from storage.qdrant import qdrant_client


class RagAgent:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.embedding_model = SentenceTransformer("all-mpnet-base-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=50,
            length_function=len,
        )
        self.documents = []
        self.collection_name = "test-rag-agent"
        self.index = qdrant_client
        self.chat_model = ChatOllama(
            model="gpt-oss:20b", temperature=0.5, base_url="http://ollama:11434"
        )
        self._load_and_build_index()

    def _load_and_build_index(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: Data file not found at {self.data_path}")
            # 建立一個空的 data.txt 檔案以避免後續錯誤
            with open(self.data_path, "w", encoding="utf-8") as f:
                f.write(
                    "This is a placeholder file. Please add your knowledge base content here."
                )
            text = "This is a placeholder file. Please add your knowledge base content here."

        # 將文本轉換為 LangChain Document 對象
        docs = [Document(page_content=text)]

        # 分割文本
        self.documents = self.text_splitter.split_documents(docs)
        print(f"Data split into {len(self.documents)} chunks.")

        # 生成嵌入
        print("Generating embeddings for document chunks...")
        embeddings = self.embedding_model.encode(
            [doc.page_content for doc in self.documents], convert_to_tensor=False
        )

        # 建立 collection（一次性）
        dim = len(embeddings[0])
        self.index.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=model_qdrant.VectorParams(
                size=dim, distance=model_qdrant.Distance.COSINE
            ),
        )

        # 上傳所有 chunk
        points = []
        for idx, (doc, vector) in enumerate(zip(self.documents, embeddings)):
            points.append(
                model_qdrant.PointStruct(
                    id=idx, vector=vector, payload={"text": doc.page_content}
                )
            )

        self.index.upsert(collection_name=self.collection_name, points=points)
        print("Qdrant index built successfully.")

    def _retrieve_context(self, query: str, k: int = 3) -> list[str]:
        print(f"Retrieving context for query: '{query}'")
        query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)
        hits = self.index.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),  # 要轉成 list[float]
            limit=k,
        )

        retrieved_docs = [hit.payload["text"] for hit in hits]

        print(f"Retrieved {len(retrieved_docs)} documents.")

        return retrieved_docs

    def llm(self, query: str, context: str) -> list[str]:
        prompt = ChatPromptTemplate.from_template(
            """
        您是一個專業的問答助理。請根據以下提供的上下文來回答問題。
        如果上下文中沒有足夠的資訊，請回答「根據我所擁有的資料，我無法回答這個問題。」
        請不要編造答案。

        上下文 :
        ---
        {context}
        ---

        問題 : {query}

        答案 :


        """
        )
        chain = prompt | self.chat_model

        reply = chain.invoke(
            {
                "context": context,
                "query": query,
            },
        )
        return reply

    async def arun(self, query: str) -> str:
        """
        異步執行 RAG 流程。

        Args:
            query (str): 使用者的問題。

        Returns:
            str: 由 LLM 生成的答案。
        """

        context = self._retrieve_context(query, 3)

        print(f"Retrieving context for query: '{context}'")
        # query_vector = self.embedding_model.encode([query], convert_to_tensor=False)
        return self.llm(query, context)


async def main():
    """
    主函數，用於演示 RagAgent 的使用。
    """
    # 知識庫檔案的路徑
    data_file = os.path.join(os.path.dirname(__file__), "data.md")

    # 創建 RagAgent 實例
    agent = RagAgent(data_path=data_file)

    # 模擬使用者提問
    question = "雷之呼吸總共有多少型"
    print("\n--- Asking Question ---")
    print(f"Question: {question}")

    # 執行 RAG Agent 並取得答案
    answer = await agent.arun(question)

    print("\n--- Agent's Answer ---")
    print(answer)


if __name__ == "__main__":
    # 由於這是一個異步應用，我們使用 asyncio.run() 來執行主函數
    asyncio.run(main())
