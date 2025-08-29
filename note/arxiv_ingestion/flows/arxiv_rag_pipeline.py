from api.schemas.SystemSetting import SystemSettings
from arxiv_ingestion.tasks.evaluate import evaluate
from arxiv_ingestion.tasks.llm import llm
from arxiv_ingestion.tasks.prompt import build_prompt
from arxiv_ingestion.tasks.rerank import re_ranking
from arxiv_ingestion.tasks.retrieval import retrieval
from prefect import flow, get_run_logger


# --- Full RAG pipeline ---
@flow(name="Arxiv Paper RAG Pipeline")
def rag(query: str, system_settings: SystemSettings, user_id: str = "anonymous") -> str:
    logger = get_run_logger()
    logger.info("Step 1: Retrieval")
    retrieved_chunks, msg = retrieval.submit(
        query, top_k=system_settings.top_k
    ).result()

    if retrieved_chunks:
        logger.info("Step 2: Re-ranking ")
        logger.info(msg)
        logger.info(f"retrieved_chunks {retrieved_chunks[0].keys()}")

        reranked = re_ranking.submit(retrieved_chunks, query).result()

        logger.info("Step 3: Evaluation")
        eval_metrics = evaluate.submit(
            reranked, query, top_k=system_settings.top_k
        ).result()
        logger.info(f"Evaluation metrics: {eval_metrics}")

        logger.info("Step 4: Build context")
        context = build_prompt.submit(query, reranked).result()
    else:
        logger.warning("No chunks retrieved, fallback to query as prompt")

        context = ""
    prompt = query

    logger.info(f"Step 5: LLM generation with context = {context}")
    answer = llm.submit(
        context,
        prompt,
        user_language=system_settings.user_language,
        user_id=user_id,
        system_prompt=system_settings.system_prompt,
    ).result()

    logger.info(f"Answer generated: {answer[:200]}...")
    return answer


if __name__ == "__main__":
    query = "What is RAG?"
    answer = rag(
        query, system_settings=SystemSettings(user_language="Traditional Chinese")
    )
    print(answer)
