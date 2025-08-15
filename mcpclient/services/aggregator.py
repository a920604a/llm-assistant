from services.ollama import call_ollama
from conf import NOTE_API_URL
from services.mcp_client import call_note_server
import logging

logger = logging.getLogger(__name__)


def process_user_query(query: str, shortcut=True):
    # Step 1: 呼叫 Ollama LLM（主要語言理解與生成）
    if shortcut:
        llm_reply = call_ollama("gpt-oss:20b", query)
        logger.info(f"llm_reply {llm_reply}")
        return llm_reply
    else:  # rag
        # re-write user query
        llm_prompt = f"使用者說: {query}，請整理為清晰簡短的內容"
        llm_reply = call_ollama("gpt-oss:20b", llm_prompt)
        logger.info(f"Step 1: 呼叫 Ollama LLM（主要語言理解與生成） {llm_reply}")

        # Step 2: 呼叫 MCP Server（此例為筆記服務）
        logger.info(f"Step 2: 呼叫 MCP Server（此例為筆記服務）")

        note_result = call_note_server(NOTE_API_URL, {"text": llm_reply})
        logger.info(f"note_result {note_result}")

        # Step 3: 整合結果
        return note_result
