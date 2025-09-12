from api.schemas.SystemSetting import SystemSettings
from logger import AppLogger
from services.langchain_client import llm, rewrite_query
from services.store_chat_and_usage import store_chat_and_usage

logger = AppLogger(__name__).get_logger()


def llm_flow(query: str, user_id: str, system_setting: SystemSettings):
    llm_rewrite_query = rewrite_query(query=query, user_id=user_id)
    resp = llm(llm_rewrite_query, system_setting, user_id)
    logger.info(f"llm_reply {resp}")

    store_chat_and_usage(user_id, query, llm_rewrite_query, resp)

    return resp.content
