import json
from typing import List, Tuple

from api.schemas.ask import AskResponse
from api.schemas.SystemSetting import SystemSettings
from dependencies import LangchainDep, OllamaDep, QdrantDep
from embedding import get_embedding
from evaluate import evaluate
from logger import AppLogger
from prompt import build_prompt
from services.rerank import re_ranking
from services.store_chat_and_usage import store_chat_and_usage

logger = AppLogger(__name__).get_logger()


# --- Helper function: retrieval + rerank + evaluation ---
def retrieval_pipeline(
    query: str,
    system_settings: SystemSettings,
    qdrant_client: QdrantDep,
) -> Tuple[List[dict], List[str], str]:
    logger.info("Step 0: Re write ")
    # query = langchain_client.rewrite_query(query, user_id)

    query_embedding = get_embedding(query)

    logger.info("Step 1: Retrieval")
    chunks, sources, msg = qdrant_client.search(
        query=query,
        query_vector=query_embedding,
        size=system_settings.top_k,
        min_score=0.3,
    )

    if not chunks:
        logger.warning("No chunks retrieved, fallback to query as prompt")
        return [], [], ""

    logger.info("Step 2: Re-ranking ")
    logger.info(msg)
    reranked = re_ranking(chunks, query)

    logger.info("Step 3: Evaluation")
    eval_metrics = evaluate(qdrant_client, reranked, query, top_k=system_settings.top_k)
    logger.info(f"Evaluation metrics: {eval_metrics}")

    logger.info("Step 4: Build context")
    context = build_prompt(query, reranked)

    return reranked, sources, context


# --- Full RAG pipeline ---
def ask_flow(
    query: str,
    system_settings: SystemSettings,
    langchain_client: LangchainDep,
    qdrant_client: QdrantDep,
    user_id: str = "anonymous",
) -> AskResponse:
    logger.info("Step 0: Re write ")

    reranked_chunks, sources, context = retrieval_pipeline(
        query, system_settings, qdrant_client
    )

    if not reranked_chunks:
        response = AskResponse(
            query=query,
            answer="I couldn't find any relevant information in the papers to answer your question.",
            sources=[],
            chunks_used=0,
            search_mode="hybrid",
        )
        return response

    # logger.info("Step 2: Re-ranking ")
    # logger.info(msg)

    # reranked = re_ranking(retrieved_chunks, query)

    # logger.info("Step 3: Evaluation")
    # eval_metrics = evaluate(qdrant_client,
    #     reranked, query, top_k=system_settings.top_k
    # )
    # logger.info(f"Evaluation metrics: {eval_metrics}")

    # logger.info("Step 4: Build context")
    # context = build_prompt(query, reranked)

    logger.info(f"Step 5: LLM generation with context = {context}")
    resp = langchain_client.llm_context(
        context,
        query,
        user_language=system_settings.user_language,
        user_id=user_id,
        system_prompt=system_settings.system_prompt,
    )

    store_chat_and_usage(user_id, query, context, resp)

    # return answer
    # Prepare response
    response = AskResponse(
        query=query,
        answer=resp.content,
        sources=sources,
        chunks_used=len(reranked_chunks),
        search_mode="hybrid",
    )

    return response


async def rag_stream(
    ollama_client: OllamaDep,
    qdrant_client: QdrantDep,
    query: str,
    system_settings: SystemSettings,
    user_id: str = "anonymous",
) -> str:
    try:
        reranked_chunks, sources, context = retrieval_pipeline(
            query, system_settings, qdrant_client
        )

        if not reranked_chunks:
            yield f"data: {json.dumps({'answer': 'No relevant information found.', 'sources': [], 'done': True})}\n\n"

        logger.info(f"Step 5: LLM stream generation with context = {context}")

        async for chunk in ollama_client.generate_stream(
            prompt=context, temperature=system_settings.temperature
        ):
            # 每一個 chunk 是模型生成的一部分文字
            yield json.dumps(chunk) + "\n"

    except Exception as e:
        error_msg = {"error": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"


if __name__ == "__main__":
    query = "What is RAG?"
    answer = ask_flow(
        query, system_settings=SystemSettings(user_language="Traditional Chinese")
    )
    print(answer)
