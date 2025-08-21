from services.langchain_client import (  # 假設 llm 在 your_module.py，換成實際檔案名稱
    llm,
)


def test_llm_basic():
    """測試 llm() 能否正常呼叫 ChatOllama 並回傳內容"""

    query = "什麼是 LangChain？"

    result = llm(query, "Traditional Chinese")

    # 確認有輸出字串
    assert isinstance(result, str)
    assert len(result) > 0

    # 驗證內容是否有關鍵字（這裡用中文"LangChain"來確認）
    assert "LangChain" in result
