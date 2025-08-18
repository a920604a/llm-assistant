from workflow.rag_pipeline import retrieval, re_ranking, build_prompt, llm
from logger import get_logger

logger = get_logger(__name__)

def rag(query: str):
    # Step R: Retrieval
    retrieved = retrieval(query)
    logger.error("Step R: Retrieval %s", retrieved)

    if retrieved:


        # Step NR: Re-ranking
        reranked = re_ranking(retrieved, query)
        logger.error("Step NR: Re-ranking %s", reranked)

        # 生成 Prompt
        prompt = build_prompt(query, reranked)
        logger.error("生成 Prompt %s", prompt)
    else:
        prompt = query
    # 生成答案
    answer = llm(prompt)
    logger.error("生成答案 %s", answer)

    return answer
