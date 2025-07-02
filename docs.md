```
llm-mcp-assistant/
├── app/
│   ├── main.py              # FastAPI server
│   ├── agent/               # 所有 Agent 模組
│   │   ├── core_agent.py        # 主 LLM Agent
│   │   ├── vision_agent.py      # 圖像處理
│   │   ├── speech_agent.py      # 語音轉文字
│   │   ├── mcp_agent.py         # MCP 控制（WebSocket）
│   │   └── rag_agent.py         # Qdrant 檢索流程
│   ├── tools/              # MCP 工具函式
│   ├── config.py
│   └── llm_client.py       # Gemini / OpenRouter API Wrapper
├── data/                   # MCP 說明文檔、向量化資料
├── frontend/               # Streamlit UI (optional)
├── docker-compose.yml
├── requirements.txt
└── README.md

```