import asyncio
import json
import time
from typing import List, Tuple

from api.schemas.ask import AskResponse
from api.schemas.SystemSetting import SystemSettings
from config import get_settings
from logger import AppLogger
from services.embedding import get_embedding
from services.evaluate import evaluate
from services.langfuse.client import LangfuseTracer
from services.langfuse.tracer import RAGTracer
from services.ollama.client import OllamaClient
from services.qdrant.client import QdrantClient
from services.rerank import re_ranking
from services.store_chat_and_usage import (
    store_chat_and_ollama_usage,
    store_chat_and_usage,
)

logger = AppLogger(__name__).get_logger()


# --- Helper function: retrieval + rerank + evaluation ---
def retrieval_pipeline(
    query: str,
    system_settings: SystemSettings,
    qdrant_client: QdrantClient,
    rag_tracer: RAGTracer = None,
    trace=None,
    categories=None,
) -> Tuple[List[dict], List[str], str]:
    # logger.info("Step 0: Re write ")
    # query = langchain_client.rewrite_query(query, user_id)

    logger.info("Step 0: Embedding")
    with rag_tracer.trace_embedding(trace, query=query) as embedding_span:
        query_embedding = get_embedding(query)
    rag_tracer.end_embedding(embedding_span, query_embedding)

    logger.info("Step 1: Retrieval")
    with rag_tracer.trace_search(
        trace, query=query, top_k=system_settings.top_k
    ) as search_span:
        logger.info(f"Hybrid search enabled: {system_settings.hybrid_search}")
        chunks, sources, msg, arxiv_ids, total_hits = qdrant_client.search(
            query=query,
            query_vector=query_embedding,
            size=system_settings.top_k,
            min_score=0.3,
            hybrid=system_settings.hybrid_search,
            categories=categories,
        )
        rag_tracer.end_search(search_span, chunks, arxiv_ids, total_hits)

    if not chunks:
        logger.warning("No chunks retrieved, fallback to query as prompt")
        return [], [], ""

    logger.info("Step 2: Re-ranking ")
    logger.info(msg)
    vector_weight = 0.6
    bm25_weight = 0.3
    with rag_tracer.trace_rerank(
        trace, query=query, vector_weight=vector_weight, bm25_weight=bm25_weight
    ) as rerank_span:
        reranked = re_ranking(
            chunks,
            query,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
        )
        rag_tracer.end_rerank(rerank_span, reranked)

    logger.info("Step 3: Evaluation")
    with rag_tracer.trace_evaluate(
        trace, query=query, reranked_chunks=reranked, top_k=system_settings.top_k
    ) as eval_span:
        eval_metrics = evaluate(
            qdrant_client,
            reranked,
            query,
            top_k=system_settings.top_k,
            hybrid_search=system_settings.hybrid_search,
        )
        rag_tracer.end_evaluate(eval_span, eval_metrics)

    logger.info(f"Evaluation metrics: {eval_metrics}")

    return reranked, sources, reranked


# --- Full RAG pipeline ---
async def ask_flow(
    query: str,
    system_settings: SystemSettings,
    ollama_client: OllamaClient,
    qdrant_client: QdrantClient,
    rag_tracer: RAGTracer,
    trace=None,
    user_id: str = "anonymous",
) -> AskResponse:
    reranked_chunks, sources, reranked = retrieval_pipeline(
        query, system_settings, qdrant_client, rag_tracer, trace
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

    logger.info("Step 4: Build prompt")
    # context = build_prompt(query, reranked)
    with rag_tracer.trace_prompt_construction(trace, reranked_chunks) as prompt_span:
        try:
            prompt_data = ollama_client.prompt_builder.create_structured_prompt(
                query, reranked, system_settings.user_language
            )
            final_prompt = prompt_data["prompt"]
            logger.info(f"Structured final_prompt schema: {final_prompt}")
        except Exception:
            final_prompt = ollama_client.prompt_builder.create_rag_prompt(
                query, reranked, system_settings.user_language
            )
            logger.info(f"Structured final_prompt schema: {final_prompt}")

        rag_tracer.end_prompt(prompt_span, final_prompt)

    logger.info(f"Step 5: LLM generation with context = {final_prompt[100:]}")
    with rag_tracer.trace_generation(trace, "hybrid", final_prompt) as gen_span:
        # resp = langchain_client.llm_context(
        #     query = query,
        #     context = final_prompt,
        #     user_language=system_settings.user_language,
        #     system_prompt=system_settings.system_prompt,
        # )
        # rag_tracer.end_generation(gen_span, resp.content, "hybrid")

        parsed_response, response = await ollama_client.generate_rag_answer(
            query=query,
            chunks=reranked,
            user_language=system_settings.user_language,
            use_structured_output=False,
            temperature=system_settings.temperature,
        )
        rag_tracer.end_generation(gen_span, response, "hybrid")

    store_chat_and_usage(user_id, query, final_prompt, response)

    # return answer
    # Prepare response
    response = AskResponse(
        query=query,
        answer=parsed_response.get("answer", "Unable to generate answer"),
        sources=sources,
        chunks_used=len(reranked_chunks),
        search_mode="hybrid",
    )

    return response


async def rag_stream(
    ollama_client: OllamaClient,
    qdrant_client: QdrantClient,
    query: str,
    system_settings: SystemSettings,
    langfuse_tracer: LangfuseTracer,
    user_id: str = "anonymous",
    categories: List[str] = None,
) -> str:
    try:
        rag_tracer = RAGTracer(langfuse_tracer)
        start_time = time.time()
        with rag_tracer.trace_request(user_id, query) as trace:
            reranked_chunks, sources, reranked = retrieval_pipeline(
                query, system_settings, qdrant_client, rag_tracer, trace, categories
            )

            if not reranked_chunks:
                yield f"data: {json.dumps({'answer': 'No relevant information found.', 'sources': [], 'done': True})}\n\n"

            logger.info("Step 4: Build prompt")
            # context = build_prompt(query, reranked)
            with rag_tracer.trace_prompt_construction(
                trace, reranked_chunks
            ) as prompt_span:
                final_prompt = ollama_client.prompt_builder.create_rag_prompt(
                    query, reranked, system_settings.user_language
                )

                rag_tracer.end_prompt(prompt_span, final_prompt)

            logger.info(
                f"Step 5: LLM stream generation with final_prompt = {final_prompt}"
            )
            with rag_tracer.trace_generation(trace, "hybrid", final_prompt) as gen_span:
                full_response = ""
                final_chunk = None

                async for chunk in ollama_client.generate_stream(
                    prompt=final_prompt, temperature=system_settings.temperature
                ):
                    # 每一個 chunk 是模型生成的一部分文字

                    if chunk.get("response"):
                        text_chunk = chunk["response"]
                        full_response += text_chunk
                        yield json.dumps(chunk) + "\n\n"

                    if chunk.get("done", False):
                        rag_tracer.end_generation(gen_span, full_response, "hybrid")
                        # logger.info(f"full_response {full_response}")
                        yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"

                        final_chunk = chunk  # ← save last chunk
                        break

            rag_tracer.end_request(trace, full_response, time.time() - start_time)
            if final_chunk:
                usage = store_chat_and_ollama_usage(
                    user_id,
                    query,
                    final_chunk=final_chunk,
                    prompt=final_prompt,
                    response=full_response,
                )
                print("Token Usage:", usage)

    except Exception as e:
        error_msg = {"error": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"


async def main():
    from services.langfuse.tracer import RAGTracer

    query = "TITAN: A Trajectory-Informed Technique for Adaptive Parameter Freezing  in Large-Scale VQE"
    print(query)

    # 初始化必要設定
    system_settings = SystemSettings(
        user_language="Traditional Chinese",
        translate=True,
        system_prompt="You are a helpful assistant.",
        top_k=5,
        use_rag=True,
        subscribe_email=True,
        reranker_enabled=True,
        temperature=0.7,
    )

    # 依賴注入 (實際要改成你的專案初始化方式)
    settings = get_settings()
    qdrant_client = QdrantClient(settings)
    ollama_client = OllamaClient(settings)
    rag_tracer = RAGTracer(LangfuseTracer(settings))

    # 呼叫流程
    response = await ask_flow(
        query=query,
        system_settings=system_settings,
        ollama_client=ollama_client,
        qdrant_client=qdrant_client,
        rag_tracer=rag_tracer,
    )

    print("=== 最終回答 ===")
    print(response.answer)
    print("來源：", response.sources)


if __name__ == "__main__":
    asyncio.run(main())
