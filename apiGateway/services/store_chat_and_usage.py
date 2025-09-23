from config import settings
from services.estimate_tokens import (
    estimate_tokens,
    get_ollama_token_usage,
    get_token_estimate,
)
from storage.chat_history import insert_chat_history
from storage.set_user_token_spend import set_user_token_spend


def store_chat_and_usage(user_id: str, query: str, resp: dict):
    usage = get_token_estimate(resp, query)  # leverage query not prompt
    # insert to user table
    set_user_token_spend(user_id, usage["total_tokens"])

    insert_chat_history(
        user_id=user_id,
        input_text=query,
        output_text=resp.get("response", ""),
        input_token=usage["prompt_tokens"],
        output_token=usage["completion_tokens"],
        latency_ms=usage["latency_ms"],
        model=settings.SUMMARY_MODEL_NAME,
    )


def store_chat_and_ollama_usage(
    user_id: str, query: str, final_chunk: dict, prompt: str, response: str
):
    usage = get_ollama_token_usage(
        final_chunk=final_chunk, prompt=prompt, completion=response
    )

    set_user_token_spend(user_id, usage["total_tokens"])
    insert_chat_history(
        user_id=user_id,
        input_text=query,
        output_text=response,
        input_token=estimate_tokens(query),
        output_token=estimate_tokens(response),
        latency_ms=usage["latency_ms"],
        model=settings.SUMMARY_MODEL_NAME,
    )
