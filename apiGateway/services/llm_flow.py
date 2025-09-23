from api.schemas.SystemSetting import SystemSettings
from logger import AppLogger
from services.langfuse.tracer import RAGTracer
from services.ollama.client import OllamaClient
from services.prompts.prompts import build_prompt
from services.store_chat_and_usage import store_chat_and_usage

logger = AppLogger(__name__).get_logger()


async def llm_flow(
    query: str,
    user_id: str,
    system_setting: SystemSettings,
    ollama_client: OllamaClient,
    model: str,
    rag_tracer: RAGTracer,
    trace: None,
) -> str:
    # query = langchain_client.rewrite_query(query=query, user_id=user_id)

    with rag_tracer.trace_prompt_construction(trace, query) as prompt_span:
        prompt = build_prompt(query=query, system_setting=system_setting)
        logger.info(f"prompt {prompt}")

        rag_tracer.end_prompt(prompt_span, prompt)

    with rag_tracer.trace_generation(trace, model, prompt) as gen_span:
        resp = await ollama_client.generate(prompt)

        rag_tracer.end_generation(gen_span, resp, model)

    store_chat_and_usage(user_id, query, query, resp)

    return resp.get("response", "")
