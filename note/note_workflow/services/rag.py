from logger import get_logger
from note_workflow.rag_pipeline import build_prompt, re_ranking, retrieval
from services.langchain_client import llm_context

logger = get_logger(__name__)


def rag(query: str):
    # Step R: Retrieval
    retrieved = retrieval(query)
    logger.error("Step R: Retrieval %s", retrieved)

    if retrieved:
        # Step NR: Re-ranking
        reranked = re_ranking(retrieved, query)
        logger.error("Step NR: Re-ranking %s", reranked)

        # 生成 context
        context = build_prompt(query, reranked)
        logger.error("生成 Context %s", context)

    else:
        prompt = query
        context = ""
    # 生成答案
    answer = llm_context(context, prompt)
    logger.error("生成答案 %s", answer)

    return answer
