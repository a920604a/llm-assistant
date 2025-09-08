import asyncio
import re
from typing import Any, AsyncGenerator, Dict, List

import httpx
from config import settings
from exceptions import OllamaConnectionError, OllamaException, OllamaTimeoutError
from logger import AppLogger


def clean_json_string(s: str) -> str:
    # 移除開頭的 ```json 與結尾的 ```
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s


logger = AppLogger(__name__).get_logger()


class OllamaClient:
    """Client for interacting with Ollama local LLM service."""

    def __init__(self):
        """Initialize Ollama client with settings."""
        self.base_url = settings.OLLAMA_API_URL
        self.timeout = httpx.Timeout(float(300))

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Ollama service is healthy and responding.

        Returns:
            Dictionary with health status information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Check version endpoint for health
                response = await client.get(f"{self.base_url}/api/version")

                if response.status_code == 200:
                    version_data = response.json()
                    return {
                        "status": "healthy",
                        "message": "Ollama service is running",
                        "version": version_data.get("version", "unknown"),
                    }
                else:
                    raise OllamaException(
                        f"Ollama returned status {response.status_code}"
                    )

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama service: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"Ollama health check failed: {str(e)}")

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.

        Returns:
            List of model information dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")

                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
                else:
                    raise OllamaException(
                        f"Failed to list models: {response.status_code}"
                    )

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama service: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"Error listing models: {e}")

    # 普通非 streaming 生成
    async def generate(
        self, model: str = settings.MODEL_NAME, prompt: str = "", **kwargs
    ) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {"model": model, "prompt": prompt, "stream": False, **kwargs}
            response = await client.post(f"{self.base_url}/api/generate", json=data)
            if response.status_code == 200:
                raw = response.json()["response"]
                return clean_json_string(raw)
            else:
                raise OllamaException(f"Generation failed: {response.status_code}")

    # 原始 async generator 只負責 streaming
    async def generate_stream(
        self, model: str = settings.MODEL_NAME, prompt: str = "", **kwargs
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {"model": model, "prompt": prompt, "stream": True, **kwargs}
            async with client.stream(
                "POST", f"{self.base_url}/api/generate", json=data
            ) as response:
                if response.status_code != 200:
                    raise OllamaException(
                        f"Streaming generation failed: {response.status_code}"
                    )
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    import json

                    try:
                        chunk_data = json.loads(line)
                        if "response" in chunk_data:
                            yield clean_json_string(chunk_data["response"])
                    except json.JSONDecodeError:
                        yield line


if __name__ == "__main__":

    async def main():
        client = OllamaClient()

        # 1️⃣ 列出模型
        models = await client.list_models()
        print("=== Available models ===")
        for m in models:
            print(m)
        print("-" * 40)

        # 2️⃣ 非 streaming 生成
        query = "什麼是 LangChain？"
        full_result = await client.generate(prompt=query)
        print("=== Full Response ===")
        print(full_result)
        print("-" * 40)

        # 3️⃣ Streaming 生成
        print("=== Streaming Response ===")
        async for chunk in client.generate_stream(prompt=query):
            # 邊拿邊印
            print(chunk, end="", flush=True)
        print("\n" + "-" * 40)

    # 執行
    asyncio.run(main())
