import re
from typing import Any, Dict, List, Optional

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

    async def generate(
        self,
        model: str = settings.MODEL_NAME,
        prompt: str = "",
        stream: bool = False,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate text using specified model.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            stream: Whether to stream response (not implemented)
            **kwargs: Additional generation parameters

        Returns:
            Response dictionary or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {"model": model, "prompt": prompt, "stream": stream, **kwargs}

                response = await client.post(f"{self.base_url}/api/generate", json=data)

                if response.status_code == 200:
                    raw = response.json()["response"]
                    cleaned = clean_json_string(raw)
                    return cleaned
                else:
                    raise OllamaException(f"Generation failed: {response.status_code}")

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama service: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"Error generating with Ollama: {e}")
