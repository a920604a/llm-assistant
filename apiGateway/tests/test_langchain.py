import pytest
from api.schemas.SystemSetting import SystemSettings
from services.langchain_client import llm, rewrite_query


# 假設 SystemSettings 是 dict-like
@pytest.fixture
def sample_system_setting():
    return SystemSettings(
        user_language="English",
        translate=False,
        system_prompt="",
        top_k=5,
        use_rag=True,
        subscribe_email=False,
        reranker_enabled=True,
        temperature=0.6,  # Default temperature for LLM responses
    )


def test_llm_translate(sample_system_setting):
    sample_system_setting.translate = True
    """測試 llm() 函式，啟用翻譯模式"""
    query = "What is LangChain?"
    result = llm(query, sample_system_setting, user_id="test_user")
    assert result is not None
    print("✅ llm translate result:", getattr(result, "content", result))


def test_llm_no_translate(sample_system_setting):
    sample_system_setting.translate = False
    """測試 llm() 函式，不翻譯模式"""
    query = "What is LangChain?"
    result = llm(query, sample_system_setting, user_id="test_user")
    assert result is not None
    print("✅ llm no translate result:", getattr(result, "content", result))


def test_rewrite_query():
    """測試 rewrite_query()"""
    query = "Explain LangChain in simple terms."
    result = rewrite_query(query, user_id="test_user")
    assert isinstance(result, str)
    print("✅ rewrite_query result:", result)
