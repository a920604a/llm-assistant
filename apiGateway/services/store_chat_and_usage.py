from config import settings
from langchain_core.messages.ai import AIMessage
from services.estimate_tokens import get_token_estimate
from storage.chat_history import insert_chat_history
from storage.set_user_token_spend import set_user_token_spend


def store_chat_and_usage(user_id: str, query: str, prompt: str, resp: AIMessage):
    usage = get_token_estimate(resp, query)  # leverage query not prompt
    # insert to user table
    set_user_token_spend(user_id, usage["total_tokens"])

    insert_chat_history(
        user_id=user_id,
        input_text=query,
        output_text=resp.content,
        input_token=usage["prompt_tokens"],
        output_token=usage["completion_tokens"],
        latency_ms=usage["latency_ms"],
        model=settings.SUMMARY_MODEL_NAME,
    )
