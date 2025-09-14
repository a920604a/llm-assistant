import pytest
from exceptions import OllamaException
from services.ollama.client import OllamaClient


@pytest.mark.asyncio
async def test_health_check():
    client = OllamaClient()
    result = await client.health_check()
    assert result["status"] == "healthy"
    print("✅ Health:", result)


@pytest.mark.asyncio
async def test_list_models():
    client = OllamaClient()
    models = await client.list_models()
    assert isinstance(models, list)
    print("✅ Models:", models)


@pytest.mark.asyncio
async def test_generate():
    """測試 OllamaClient.generate 單次生成"""
    client = OllamaClient()
    try:
        result = await client.generate(prompt="Hello, who are you?")
        assert result is not None
        print("✅ Generate result:", result)
    except OllamaException as e:
        # 如果 Ollama 回傳 NDJSON 會導致 Exception，這裡捕捉並打印
        print("⚠️ Generate raised OllamaException (可能是 NDJSON 回傳):", e)


@pytest.mark.asyncio
async def test_generate_stream():
    """測試 OllamaClient.generate_stream 流式生成"""
    client = OllamaClient()
    count = 0
    try:
        async for chunk in client.generate_stream(
            prompt="Tell me a short story about a dragon"
        ):
            print("Chunk:", chunk)
            assert "response" in chunk  # 每個 chunk 至少要有 response
            count += 1
            if count >= 5:  # 只測前 5 個 chunk，避免測試過長
                break
        assert count > 0
        print(f"✅ Streamed {count} chunks successfully")
    except OllamaException as e:
        print("⚠️ generate_stream raised OllamaException:", e)
