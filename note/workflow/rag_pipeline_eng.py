from typing import List
from prefect import flow

from workflow.tasks.retrieval import retrieval
from workflow.tasks.rerank import re_ranking
from workflow.tasks.prompt import build_prompt
from workflow.tasks.llm import llm
import logging

logger = logging.getLogger(__name__)





# --- Full RAG pipeline ---
@flow(name="RAG Pipeline")
def rag(query: str, top_k: int = 5) -> str:
    logger.info("Step 1: Retrieval")
    retrieved_chunks = retrieval.submit(query, top_k=top_k).result()

    if retrieved_chunks:
        logger.info("Step 2: Re-ranking")
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
    query = "the course start?"
    answer = rag(query)
    print(answer)