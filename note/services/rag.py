from typing import List
from qdrant_client.http import models
from database.qdrant import qdrant_client
from conf import COLLECTION_NAME, OLLAMA_API_URL
from services.embedding import get_embedding
import requests


def search(query:str):
    return ""

def build_prompt(prompt:str, search_results):
    return prompt


# 召回 top k 相關分片
def retrieval(query: str, top_k: int = 5):
    # Step 1: 將 query embed 成向量（用跟 ingest 一樣的模型）
    query_vec = get_embedding(query)

    # Step 2: 使用 Qdrant 向量搜尋召回
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
    )
    # 搜尋結果是 PointStruct list，取出 text 內容
    chunks = [hit.payload.get("text", "") for hit in search_result]
    return chunks

# 重排（Re-ranking）範例（簡易用 query 字串長度排序示範）
def re_ranking(chunks: list, query: str):
    # 這裡可以用更複雜的 rerank 模型或打分，暫時依文字長度逆序
    sorted_chunks = sorted(chunks, key=lambda c: len(c), reverse=True)
    return sorted_chunks

def build_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n".join(retrieved_chunks[:3])  # 取前三段
    prompt = f"使用者問題: {query}\n相關內容:\n{context}\n請根據以上內容回答問題："
    return prompt

def llm(prompt:str,  model: str = "gpt-oss:20b"):
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



def rag(query : str):
    search_results = search(query)
    # Step R: Retrieval
    retrieved = retrieval(query)

    # Step NR: Re-ranking
    reranked = re_ranking(retrieved, query)

    # 生成 Prompt
    prompt = build_prompt(query, reranked)

    # 生成答案
    answer = llm(prompt)

    return answer