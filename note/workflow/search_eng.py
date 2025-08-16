from typing import List
import requests
import jieba
from storage.qdrant import qdrant_client
from conf import COLLECTION_NAME, OLLAMA_API_URL
from services.embedding import get_embedding
from qdrant_client import models
from conf import MODEL_NAME
import logging

logger = logging.getLogger(__name__)


# 召回 top k 相關分片
def retrieval(query: str, top_k: int = 5, course='data-engineering-zoomcamp'):

    # Step 1: 將 query embed 成向量（用跟 ingest 一樣的模型）
    query_vector = get_embedding(query)
    
    

    # Step 2: 使用 Qdrant 向量搜尋召回
    # search_result = qdrant_client.search(
    #     collection_name=COLLECTION_NAME,
    #     query_vector=query_vec,
    #     limit=top_k,
    # )

    # Step 3:# Query Qdrant
    query_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="course",
                    match=models.MatchValue(value=course)
                )
            ]
        ),
        limit=top_k,
        with_payload=True
    )

    # Extract payloads
    results = []
    for hit in query_result:
        results.append(hit.payload)

    logger.info(f"Retrieved {len(results)} chunks from collection '{COLLECTION_NAME}'")
    return results


# 重排（Re-ranking）範例（簡易用 query 字串長度排序示範）


def re_ranking(chunks: List[dict], query: str) -> List[dict]:
    query_tokens = query.lower().split()
    sorted_chunks = sorted(
        chunks,
        key=lambda c: sum(1 for token in query_tokens if token in c.get("text", "").lower()),
        reverse=True
    )
    return sorted_chunks


def build_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n".join(retrieved_chunks[:3])  # 取前三段
    # prompt = f"使用者問題: {query}\n相關內容:\n{context}\n請根據以上內容回答問題："
    prompt = f"User question: {query}\nRelevant context:\n{context}\nPlease answer the question based on the above context."

    return prompt


def llm(prompt: str, model: str = MODEL_NAME):
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["response"]


# --- Full RAG pipeline ---
def rag(query: str, top_k: int = 5) -> str:
    logger.info("Step 1: Retrieval")
    retrieved_chunks = retrieval(query, top_k=top_k)
    logger.info(f"Retrieved {len(retrieved_chunks)} chunks")

    if retrieved_chunks:
        logger.info("Step 2: Re-ranking")
        reranked_chunks = re_ranking(retrieved_chunks, query)
        logger.info(f"Top chunk after re-ranking: {reranked_chunks[0]['text'][:100]}...")

        logger.info("Step 3: Build prompt")
        # 取 top 3 chunk 的 text
        context = "\n".join([c["text"] for c in reranked_chunks[:3]])
        prompt = f"User question: {query}\nRelevant context:\n{context}\nPlease answer the question based on the above context."
        logger.info(f"Prompt:\n{prompt[:300]}...")
    else:
        logger.warning("No relevant chunks retrieved, using query as prompt")
        prompt = query

    logger.info("Step 4: LLM generation")
    answer = llm(prompt)
    logger.info(f"Generated answer: {answer[:200]}...")
    return answer

if __name__ == "__main__":
    query = "the course start?"
    answer = rag(query)
    print(answer)