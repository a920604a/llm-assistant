from api.schemas.user import UserQuery
from conf import NOTE_API_URL
from logger import get_logger
from redis_client import get_redis_system_setting
from services.langchain_client import llm, rewrite_query
from services.mcp_client import call_note_server

logger = get_logger(__name__)


def process_user_query(user_query: UserQuery, user_id: str):
    _cache = get_redis_system_setting(user_id=user_id)
    shortcut = not _cache.use_rag  # 是否使用快捷方式
    user_language = _cache.user_language
    isTranslate = _cache.translate  # 是否需要翻譯
    logger.info(
        f"process_user_query: user_id={user_id}, shortcut={shortcut}, user_language={user_language}, isTranslate={isTranslate}"
    )

    # 呼叫 Ollama LLM（主要語言理解與生成）
    if shortcut:
        llm_reply = llm(user_query.query, isTranslate, user_language)
        logger.info(f"llm_reply {llm_reply}")
        return llm_reply
    else:  # rag
        # Step 1 : re-write user query
        llm_reply = rewrite_query(user_query.query)
        logger.info(f"Step 1: 呼叫 Ollama LLM（主要語言理解與生成） {llm_reply[:200]}")

        # Step 2: 呼叫 MCP Server（筆記服務）
        logger.info("Step 2: 呼叫 MCP Server（筆記服務）")

        note_result = call_note_server(
            NOTE_API_URL,
            {"text": llm_reply, "user_id": user_id},
        )
        logger.info(f"note_result {note_result[:200]}")

        # Step 3: 整合結果
        return note_result
