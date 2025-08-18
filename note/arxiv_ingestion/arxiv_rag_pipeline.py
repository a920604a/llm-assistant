from typing import List
from prefect import flow

from tasks.retrieval import retrieval
from tasks.rerank import re_ranking
from tasks.prompt import build_prompt
from tasks.llm import llm
import logging
from prefect import get_run_logger
import math


# ---------------- 評估函數 ----------------
def ndcg_at_k(ranked_chunks: List[dict], ground_truth_ids: List[str], k: int = 5):
    """
    計算 NDCG@k
    ranked_chunks: rerank 後的 chunks，每個 chunk 需有 'id' 欄位
    ground_truth_ids: 真實相關 chunk id list
    """
    dcg = 0.0
    for i, chunk in enumerate(ranked_chunks[:k]):
        if chunk.get("id") in ground_truth_ids:
            dcg += 1.0 / math.log2(i + 2)  # i 從 0 開始
    # 計算理想 DCG
    ideal_dcg = sum(
        1.0 / math.log2(i + 2) for i in range(min(k, len(ground_truth_ids)))
    )
    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def mrr_at_k(ranked_chunks: List[dict], ground_truth_ids: List[str], k: int = 5):
    """
    計算 MRR@k
    """
    for i, chunk in enumerate(ranked_chunks[:k]):
        if chunk.get("id") in ground_truth_ids:
            return 1.0 / (i + 1)
    return 0.0


# --- Full RAG pipeline ---
@flow(name="Arxiv Paper RAG Pipeline")
def rag(query: str, top_k: int = 5) -> str:
    logger = get_run_logger()
    logger.info("Step 1: Retrieval")
    retrieved_chunks, msg = retrieval.submit(query, top_k=top_k).result()

    if retrieved_chunks:
        logger.info("Step 2: Re-ranking ")
        logger.info(msg)

        reranked = re_ranking.submit(retrieved_chunks, query).result()

        logger.info("Step 3: Build context ")
        context = build_prompt.submit(query, reranked).result()
    else:
        logger.warning("No chunks retrieved, fallback to query as prompt")
        prompt = query
        context = ""

    logger.info("Step 4: LLM generation")
    answer = llm.submit(context, prompt).result()

    logger.info(f"Answer generated: {answer[:200]}...")
    return answer


if __name__ == "__main__":
    query = "What is Planning Agents on an Ego-Trip"
    answer = rag(query)
    print(answer)
