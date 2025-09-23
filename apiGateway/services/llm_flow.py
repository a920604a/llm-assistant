from api.schemas.SystemSetting import SystemSettings
from logger import AppLogger
from services.langchain.client import LangChainClient
from services.store_chat_and_usage import store_chat_and_usage

logger = AppLogger(__name__).get_logger()


def llm_flow(
    query: str,
    user_id: str,
    system_setting: SystemSettings,
    langchain_client: LangChainClient,
) -> str:
    # query = langchain_client.rewrite_query(query=query, user_id=user_id)
    resp = langchain_client.llm(query, system_setting, user_id)
    logger.info(f"llm_reply {resp}")

    store_chat_and_usage(user_id, query, query, resp)

    return resp.content
