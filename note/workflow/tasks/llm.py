import requests
from prefect import task
from conf import OLLAMA_API_URL, MODEL_NAME

@task
def llm(prompt: str, model: str = MODEL_NAME) -> str:
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        # timeout=100
    )
    response.raise_for_status()
    return response.json().get("response", "")


