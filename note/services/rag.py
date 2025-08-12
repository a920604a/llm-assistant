from typing import List


def search(query:str):
    return ""

def build_prompt(prompt:str, search_results):
    return prompt


def rerank(chunks: List[str], query: str) -> List[str]:
    """簡單重排：依 query 裡面詞數在 chunk 出現頻率排序"""
    def score(chunk):
        return sum(chunk.count(word) for word in query.split())
    return sorted(chunks, key=score, reverse=True)

def build_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n".join(retrieved_chunks[:3])  # 取前三段
    prompt = f"使用者問題: {query}\n相關內容:\n{context}\n請根據以上內容回答問題："
    return prompt

def llm(prompt:str):
    
    return result


def rag(query : str):
    search_results = search(query)
    # Step R: Retrieval
    retrieved = retrieval(query)

    # Step NR: Re-ranking
    reranked = rerank(retrieved, query)

    # 生成 Prompt
    prompt = build_prompt(query, reranked)

    # 生成答案
    answer = llm(prompt)

    return answer