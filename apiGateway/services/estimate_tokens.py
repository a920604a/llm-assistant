def estimate_tokens(text: str) -> int:
    """
    粗略估算 token 數量
    假設平均每 token 約 4 個字元（英文）
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def get_token_estimate(resp, prompt: str):
    """
    resp: dict
    prompt: 組裝好的 prompt 字串
    """
    # Input token（prompt）
    prompt_tokens = estimate_tokens(prompt)

    # Output token（回傳內容）
    output_tokens = estimate_tokens(resp.get("response", ""))

    total_tokens = prompt_tokens + output_tokens

    # 延遲
    latency_ms = None
    total_duration_ns = resp.get("total_duration")
    if total_duration_ns:
        latency_ms = total_duration_ns / 1_000_000  # ns -> ms

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
    }


def get_ollama_token_usage(
    final_chunk: dict, prompt: str = None, completion: str = None
):
    """
    Extract token usage and latency info from Ollama's final response chunk.

    final_chunk: dict
        The last Ollama response JSON (must include "done": true).
        Example:
        {
            "done": true,
            "eval_count": 25,
            "prompt_eval_count": 8,
            "total_duration": 12345678
        }
    prompt: str (optional)
        Original prompt string, only used for debugging/logging.
    completion: str (optional)
        Final model output, only used for debugging/logging.
    """
    prompt_tokens = final_chunk.get("prompt_eval_count", 0)
    completion_tokens = final_chunk.get("eval_count", 0)
    total_tokens = prompt_tokens + completion_tokens

    latency_ms = None
    if "total_duration" in final_chunk:
        latency_ms = final_chunk["total_duration"] / 1_000_000  # ns → ms

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
    }
