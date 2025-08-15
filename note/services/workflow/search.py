from typing import List
import requests
import jieba
from storage.qdrant import qdrant_client
from conf import COLLECTION_NAME, OLLAMA_API_URL
from services.embedding import get_embedding
from qdrant_client import models
from conf import MODEL_NAME

# 召回 top k 相關分片
def retrieval(query: str, top_k: int = 5):
    # 中文分詞
    query_tokens = " ".join(jieba.cut(query))

    # Step 1: 將 query embed 成向量（用跟 ingest 一樣的模型）
    query_vec = get_embedding(query)

    # Step 2: 使用 Qdrant 向量搜尋召回
    # search_result = qdrant_client.search(
    #     collection_name=COLLECTION_NAME,
    #     query_vector=query_vec,
    #     limit=top_k,
    # )

    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="bm25_text", match=models.MatchText(text=query_tokens)
                )
            ]
        ),
        limit=top_k,
    )

    # 搜尋結果是 PointStruct list，取出 text 內容
    chunks = [hit.payload.get("text", "") for hit in search_result]
    return chunks


# 重排（Re-ranking）範例（簡易用 query 字串長度排序示範）
def re_ranking(chunks: List[str], query: str) -> List[str]:
    # 簡單示例：依 query 關鍵字數量排序
    sorted_chunks = sorted(
        chunks, key=lambda c: sum(1 for kw in query if kw in c), reverse=True
    )
    return sorted_chunks


def build_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n".join(retrieved_chunks[:3])  # 取前三段
    prompt = f"使用者問題: {query}\n相關內容:\n{context}\n請根據以上內容回答問題："
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
