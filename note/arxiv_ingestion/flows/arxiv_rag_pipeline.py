from api.schemas.SystemSetting import SystemSettings
from arxiv_ingestion.tasks.evaluate import evaluate
from arxiv_ingestion.tasks.llm import llm, rewrite
from arxiv_ingestion.tasks.prompt import build_prompt
from arxiv_ingestion.tasks.rerank import re_ranking
from arxiv_ingestion.tasks.retrieval import retrieval
from logger import AppLogger
from services.store_chat_and_usage import store_chat_and_usage

logger = AppLogger(__name__).get_logger()


# --- Full RAG pipeline ---
def rag(query: str, system_settings: SystemSettings, user_id: str = "anonymous") -> str:
    logger.info("Step 0: Re write ")
    llm_rewrite_query = rewrite(query, user_id)

    logger.info("Step 1: Retrieval")
    retrieved_chunks, msg = retrieval(llm_rewrite_query, top_k=system_settings.top_k)

    if retrieved_chunks:
        logger.info("Step 2: Re-ranking ")
        logger.info(msg)
        logger.info(f"retrieved_chunks {retrieved_chunks[0].keys()}")

        reranked = re_ranking(retrieved_chunks, llm_rewrite_query)

        logger.info("Step 3: Evaluation")
        eval_metrics = evaluate(
            reranked, llm_rewrite_query, top_k=system_settings.top_k
        )
        logger.info(f"Evaluation metrics: {eval_metrics}")

        logger.info("Step 4: Build context")
        context = build_prompt(llm_rewrite_query, reranked)
    else:
        logger.warning("No chunks retrieved, fallback to query as prompt")

        context = ""

    logger.info(f"Step 5: LLM generation with context = {context}")
    resp = llm(
        context,
        llm_rewrite_query,
        user_language=system_settings.user_language,
        user_id=user_id,
        system_prompt=system_settings.system_prompt,
    )

    answer = resp.content

    logger.info(f"Answer generated: {answer[:200]}...")
    logger.info(f"query: {query}...")
    logger.info(f"prompt: {llm_rewrite_query}...")

    store_chat_and_usage(user_id, query, llm_rewrite_query, resp)

    return answer


if __name__ == "__main__":
    query = "What is RAG?"
    answer = rag(
        query, system_settings=SystemSettings(user_language="Traditional Chinese")
    )
    print(answer)
