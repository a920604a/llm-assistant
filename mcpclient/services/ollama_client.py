import requests
from conf import MODEL_NAME, OLLAMA_API_URL
from logger import get_logger
from utils import clean_json_string

logger = get_logger(__name__)


def call_ollama(prompt: str) -> str:
    logger.info(f"呼叫 Ollama 模型 {MODEL_NAME}，prompt: {prompt}")
    # TODO: 改成實際呼叫 Ollama API
    logger.info(f"call_ollama {OLLAMA_API_URL}/api/generate")

    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
    )
    logger.info(f"response {response}")
    response.raise_for_status()
    raw = response.json()["response"]

    cleaned = clean_json_string(raw)
    logger.info(f"cleaned {cleaned}")

    return cleaned
