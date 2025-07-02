import os
import requests
from openai import OpenAI

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528-qwen3-8b:free")

def ask_llm(prompt: str, context: str = "") -> str:
    if LLM_PROVIDER == "gemini":
        return ask_gemini(prompt, context)
    elif LLM_PROVIDER == "openrouter":
        return ask_openrouter(prompt, context)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def ask_gemini(prompt: str, context: str = "") -> str:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }
    payload = {
        "contents": [
            {
                "parts": [{"text": full_prompt}]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Gemini error] {e}, raw response: {result}"


def ask_openrouter(prompt: str, context: str = "") -> str:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    completion = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        
        extra_body={
        "models": ["anthropic/claude-3.5-sonnet", "gryphe/mythomax-l2-13b"]
            },
        messages=[
            {"role": "system", "content": "你是一位智慧的多模態任務助理。"},
            {"role": "user", "content": full_prompt}
        ]
    )
    return completion.choices[0].message.content
