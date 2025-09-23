import json
import time

from config import settings
from logger import AppLogger
from redis_client import get_redis_system_setting
from services.langfuse.client import LangfuseTracer
from services.langfuse.tracer import RAGTracer
from services.llm_flow import llm_flow
from services.ollama.client import OllamaClient
from services.prompts.prompts import build_prompt
from services.rag.rag_client import call_note_server, call_note_stream_server
from services.store_chat_and_usage import store_chat_and_ollama_usage

logger = AppLogger(__name__).get_logger()


async def process_user_query(
    query: str,
    user_id: str,
    ollama_client: OllamaClient,
    langfuse_tracer: LangfuseTracer,
    model: str,
) -> str:
    _cache = get_redis_system_setting(user_id=user_id)
    shortcut = not _cache.use_rag  # 是否使用快捷方式

    # 呼叫 Ollama LLM（主要語言理解與生成）
    logger.info(f"query {query}")
    if shortcut:
        rag_tracer = RAGTracer(langfuse_tracer)
        start_time = time.time()
        with rag_tracer.trace_request(user_id, query) as trace:
            llm_reply = await llm_flow(
                query=query,
                user_id=user_id,
                system_setting=_cache,
                ollama_client=ollama_client,
                model=model,
                rag_tracer=rag_tracer,
                trace=trace,
            )

            rag_tracer.end_request(trace, llm_reply, time.time() - start_time)

        return llm_reply
    else:  # rag
        # 呼叫 MCP Server（筆記服務）
        logger.info("呼叫 MCP Server（筆記服務）")

        note_result = await call_note_server(
            settings.NOTE_API_URL,
            {"text": query, "user_id": user_id},
        )
        # logger.info(f"note_result {note_result[:200]}")
        logger.info(f"note_result {note_result}")

        # Step 3: 整合結果

        return note_result


async def generate_stream(
    query: str,
    user_id: str,
    ollama_client: OllamaClient,
    langfuse_tracer: LangfuseTracer,
    model: str,
):
    try:
        _cache = get_redis_system_setting(user_id=user_id)
        shortcut = not _cache.use_rag
        logger.info(f"query {query}")
        if shortcut:
            rag_tracer = RAGTracer(langfuse_tracer)
            start_time = time.time()
            with rag_tracer.trace_request(user_id, query) as trace:
                # query = langchain_client.rewrite_query(query=query, user_id=user_id)
                with rag_tracer.trace_prompt_construction(trace, query) as prompt_span:
                    prompt = build_prompt(query, _cache)
                    logger.info(f"prompt {prompt}")
                    rag_tracer.end_prompt(prompt_span, prompt)
                # full_response = ""
                # 丟到 LLM，使用 streaming 介面

                with rag_tracer.trace_generation(trace, model, prompt) as gen_span:
                    full_response = ""
                    final_chunk = None

                    async for chunk in ollama_client.generate_stream(
                        prompt=prompt, temperature=_cache.temperature
                    ):
                        # 每一個 chunk 是模型生成的一部分文字

                        if chunk.get("response"):
                            text_chunk = chunk["response"]
                            full_response += text_chunk
                            # yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"
                            yield text_chunk

                        if chunk.get("done", False):
                            # yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"
                            rag_tracer.end_generation(gen_span, full_response, model)
                            final_chunk = chunk
                            break
                rag_tracer.end_request(trace, full_response, time.time() - start_time)

                store_chat_and_ollama_usage(
                    user_id,
                    query,
                    final_chunk=final_chunk,
                    prompt=prompt,
                    response=full_response,
                )

        else:
            # 呼叫 MCP Server（筆記服務）
            logger.info("呼叫 MCP Server（筆記服務）")

            async for chunk in call_note_stream_server(
                settings.NOTE_API_URL,
                {"text": query, "user_id": user_id},
            ):
                if chunk.get("chunk"):
                    text_chunk = chunk["chunk"]
                    yield text_chunk

                if chunk.get("answer", False):
                    break

    except Exception as e:
        error_msg = {"error": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"
