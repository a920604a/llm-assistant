
def ask_llm(prompt: str, context: list = None, provider="gemini"):
    """根據 provider 使用 Gemini 或 OpenRouter 調用 LLM"""
    if provider == "gemini":
        return call_gemini(prompt, context)
    elif provider == "openrouter":
        return call_openrouter(prompt, context)
    else:
        return "Unsupported LLM provider"

# TODO: 實作 Gemini / OpenRouter API 呼叫

def call_gemini(prompt, context):
    # 串接 Gemini 1.5 Pro API
    return f"[Gemini 回答內容 for: {prompt}]"

def call_openrouter(prompt, context):
    # 串接 OpenRouter GPT-4o or Claude 等模型
    return f"[OpenRouter 回答內容 for: {prompt}]"