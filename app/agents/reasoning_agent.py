from agents.knowledge_retriever import retrieve_docs, format_context
from tools.llm_client import ask_llm
import logging

logger = logging.getLogger(__name__)


async def process_task(task_params):
    text = task_params.get("text") or ""
    ocr = task_params.get("ocr_text") or ""
    img = task_params.get("image_desc") or ""

    final_prompt = f"來自圖片：{img}\nOCR：{ocr}\n\n使用者輸入：{text}"
    logger.info(f"Final prompt for LLM: {final_prompt}")
    context = retrieve_docs(final_prompt)
    response = ask_llm(final_prompt, context=format_context(context))
    
    return response