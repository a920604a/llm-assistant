import json
from typing import Any, Dict, List, Optional

import httpx
from config import settings
from exceptions import OllamaConnectionError, OllamaException, OllamaTimeoutError
from logger import AppLogger
from utils import clean_json_string

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
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate text using specified model.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            **kwargs: Additional generation parameters

        Returns:
            Response dictionary or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {"model": model, "prompt": prompt, **kwargs}

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

    async def generate_stream(
        self, model: str = settings.MODEL_NAME, prompt: str = "", **kwargs
    ):
        """
        Generate text with streaming response.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            **kwargs: Additional generation parameters

        Yields:
            JSON chunks from streaming response
        """
        try:
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
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                yield chunk
                            except json.JSONDecodeError:
                                logger.warning(
                                    f"Failed to parse streaming chunk: {line}"
                                )
                                continue

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama service: {e}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout: {e}")
        except OllamaException:
            raise
        except Exception as e:
            raise OllamaException(f"Error in streaming generation: {e}")
