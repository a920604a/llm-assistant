import asyncio
import json
from typing import Any, Dict, List

import httpx
from config import Settings
from exceptions import OllamaConnectionError, OllamaException, OllamaTimeoutError
from logger import AppLogger
from services.prompts.prompts import RAGPromptBuilder, ResponseParser

logger = AppLogger(__name__).get_logger()


class OllamaClient:
    """Client for interacting with Ollama local LLM service."""

    def __init__(self, settings: Settings):
        """Initialize Ollama client with settings."""
        self.base_url = settings.OLLAMA_API_URL
        self.model_name = settings.MODEL_NAME
        self.timeout = httpx.Timeout(float(settings.OLLAMA_TIMEOUT))
        self.prompt_builder = RAGPromptBuilder()
        self.response_parser = ResponseParser()

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
        prompt: str = "",
        **kwargs,
    ) -> str:
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
                data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs,
                }
                logger.info(f"ollama data {data}")

                response = await client.post(f"{self.base_url}/api/generate", json=data)

                if response.status_code == 200:
                    logger.info(f"ollama reponse {response.json()}")
                    return response.json()
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

    async def generate_stream(self, prompt: str = "", **kwargs):
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
                data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    **kwargs,
                }

                logger.info(f"Starting streaming generation: model={self.model_name}")

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

    async def generate_rag_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        use_structured_output: bool = False,
        temperature: float = 0.5,
        user_language: str = "English",
    ) -> Dict[str, Any]:
        """
        Generate a RAG answer using retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved document chunks with metadata
            model: Model to use for generation
            use_structured_output: Whether to use Ollama's structured output feature

        Returns:
            Dictionary with answer, sources, confidence, and citations
        """
        try:
            if use_structured_output:
                # Use structured output with Pydantic model
                prompt_data = self.prompt_builder.create_structured_prompt(
                    query, chunks, user_language=user_language
                )

                logger.info(f"prompt_data {prompt_data}\n\n")
                # Generate with structured format
                response = await self.generate(
                    prompt=prompt_data["prompt"],
                    temperature=temperature,
                    top_p=0.9,
                    # format=prompt_data["format"],
                )
            else:
                # Fallback to plain text mode
                prompt = self.prompt_builder.create_rag_prompt(
                    query, chunks, user_language=user_language
                )

                logger.info(f"promptprompt {prompt}")
                # Generate without format restrictions
                response = await self.generate(
                    prompt=prompt,
                    temperature=temperature,
                    top_p=0.9,
                )

            if response and "response" in response:
                answer_text = response["response"]
                logger.info(f"Raw LLM response: {answer_text}")

                if use_structured_output:
                    # Try to parse structured response if enabled
                    parsed_response = self.response_parser.parse_structured_response(
                        answer_text
                    )
                    logger.info(f"Parsed response:  {parsed_response}")
                    return parsed_response, response
                else:
                    # For plain text response, build simple response structure
                    sources = []
                    seen_urls = set()
                    for chunk in chunks:
                        arxiv_id = chunk.get("arxiv_id")
                        if arxiv_id:
                            arxiv_id_clean = (
                                arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
                            )
                            pdf_url = f"https://arxiv.org/pdf/{arxiv_id_clean}.pdf"
                            if pdf_url not in seen_urls:
                                sources.append(pdf_url)
                                seen_urls.add(pdf_url)

                    citations = list(
                        set(
                            chunk.get("arxiv_id")
                            for chunk in chunks
                            if chunk.get("arxiv_id")
                        )
                    )

                    return {
                        "answer": answer_text,
                        "sources": sources,
                        "confidence": "medium",
                        "citations": citations[:5],
                    }, response
            else:
                raise OllamaException("No response generated from Ollama")

        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            raise OllamaException(f"Failed to generate RAG answer: {e}")


async def main():
    from config import get_settings

    client = OllamaClient(get_settings())

    # --------------------------
    # 1️⃣ 健康檢查
    # --------------------------
    try:
        health = await client.health_check()
        logger.info(f"✅ Health check: {health}")
    except Exception as e:
        logger.info(f"❌ Health check failed: {e}")

    # --------------------------
    # 2️⃣ 列出模型
    # --------------------------
    try:
        models = await client.list_models()
        logger.info(f"✅ Available models: {models}")
    except Exception as e:
        logger.info(f"❌ List models failed: {e}")

    # --------------------------
    # 3️⃣ 生成文字
    # --------------------------
    try:
        result = await client.generate(
            model="gpt-oss:20b", prompt="Hello, who are you?"
        )
        logger.info(f"✅ Generate result: {result}")
    except Exception as e:
        logger.info(f"❌ Generate failed: {e}")

    # --------------------------
    # 4️⃣ 生成文字（串流）
    # --------------------------
    try:
        logger.info("✅ Streaming result:")
        async for chunk in client.generate_stream(
            model="gpt-oss:20b", prompt="Tell me a story about a dragon"
        ):
            logger.info(f"Chunk: {chunk}")
    except Exception as e:
        logger.info(f"❌ Streaming failed: {e}")


async def format_llm():
    from config import get_settings
    from services.prompts.prompts import ResponseParser

    settings = get_settings()

    prompt = """
        Context: TITAN is a technique for adaptive parameter freezing in VQE.

        Question: What is TITAN?

        Instructions:
        - Fill the fields based ONLY on the provided context.
        - Do NOT add extra text, explanations, or formatting outside this JSON.
        - If the context is insufficient, say so in the "answer" field.
        """

    data = {
        "model": settings.MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        # "format": RAGResponse.model_json_schema(),  # <-- 使用 format 強制 JSON 輸出
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(f"{settings.OLLAMA_API_URL}/api/generate", json=data)
        resp.raise_for_status()
        result = resp.json()

    # Ollama 回傳的文本
    llm_output = result.get("response") or result.get("text") or ""

    # 用 Pydantic 驗證
    try:
        parsed = ResponseParser.parse_structured_response(llm_output)
        print(parsed)
    except Exception as e:
        print("JSON 解析失敗:", e)
        print("LLM 原始輸出:", llm_output)


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(format_llm())
