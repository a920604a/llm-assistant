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
    resp: AIMessage
    prompt: 組裝好的 prompt 字串
    """
    # Input token（prompt）
    prompt_tokens = estimate_tokens(prompt)

    # Output token（回傳內容）
    output_tokens = estimate_tokens(resp.get("response", ""))

    total_tokens = prompt_tokens + output_tokens

    # 延遲
    latency_ms = None
    if hasattr(resp, "response_metadata"):
        total_duration_ns = resp.response_metadata.get("total_duration")
        if total_duration_ns:
            latency_ms = total_duration_ns / 1_000_000  # ns -> ms

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
    }
