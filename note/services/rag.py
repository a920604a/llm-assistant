import requests
import logging

from services.workflow.search import retrieval, re_ranking, build_prompt, llm

logger = logging.getLogger(__name__)


def rag(query: str):
    # Step R: Retrieval
    retrieved = retrieval(query)
    logger.info("Step R: Retrieval %s", retrieved)

    # Step NR: Re-ranking
    reranked = re_ranking(retrieved, query)
    logger.info("Step NR: Re-ranking %s", reranked)

    # 生成 Prompt
    prompt = build_prompt(query, reranked)
    logger.info("生成 Prompt %s", prompt)

    # 生成答案
    answer = llm(prompt)
    logger.info("生成答案 %s", answer)

    return answer
