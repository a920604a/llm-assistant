from typing import List
from prefect import flow

from tasks.retrieval import retrieval
from tasks.rerank import re_ranking
from tasks.prompt import build_prompt
from tasks.llm import llm
import logging
from prefect import get_run_logger




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

        logger.info("Step 3: Build prompt")
        prompt = build_prompt.submit(query, reranked).result()
    else:
        logger.warning("No chunks retrieved, fallback to query as prompt")
        prompt = query

    logger.info("Step 4: LLM generation")
    answer = llm.submit(prompt).result()

    logger.info(f"Answer generated: {answer[:200]}...")
    return answer


if __name__ == "__main__":
    query = "What is Planning Agents on an Ego-Trip"
    answer = rag(query)
    print(answer)