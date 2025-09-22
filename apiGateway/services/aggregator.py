import json

from config import settings
from logger import AppLogger
from redis_client import get_redis_system_setting
from services.langchain_client import rewrite_query
from services.llm_flow import llm_flow
from services.note_client import call_note_server, call_note_stream_server
from services.ollama_client import OllamaClient
from services.prompts import build_prompt

logger = AppLogger(__name__).get_logger()


def process_user_query(query: str, user_id: str) -> str:
    _cache = get_redis_system_setting(user_id=user_id)
    shortcut = not _cache.use_rag  # 是否使用快捷方式

    # 呼叫 Ollama LLM（主要語言理解與生成）
    logger.info(f"query {query}")
    if shortcut:
        llm_reply = llm_flow(query, user_id, _cache)

        return llm_reply
    else:  # rag
        # 呼叫 MCP Server（筆記服務）
        logger.info("呼叫 MCP Server（筆記服務）")

        note_result = call_note_server(
            settings.NOTE_API_URL,
            {"text": query, "user_id": user_id},
        )
        # logger.info(f"note_result {note_result[:200]}")
        logger.info(f"note_result {note_result}")

        # Step 3: 整合結果

        return note_result


async def generate_stream(query: str, user_id: str):
    try:
        ollama_clinet = OllamaClient()
        _cache = get_redis_system_setting(user_id=user_id)
        shortcut = not _cache.use_rag
        logger.info(f"query {query}")
        if shortcut:
            query = rewrite_query(query=query, user_id=user_id)
            prompt = build_prompt(query, _cache)
            logger.info(f"prompt {prompt}")
            # full_response = ""
            # 丟到 LLM，使用 streaming 介面
            async for chunk in ollama_clinet.generate_stream(
                prompt=prompt, temperature=_cache.temperature
            ):
                # 每一個 chunk 是模型生成的一部分文字

                if chunk.get("response"):
                    text_chunk = chunk["response"]
                    # full_response += text_chunk
                    # yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"
                    yield text_chunk

                if chunk.get("done", False):
                    # yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"
                    break

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
