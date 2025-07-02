```
llm-mcp-assistant/
├── app/
│   ├── main.py              # FastAPI server
│   ├── agents/               # 所有 Agent 模組
│   │   ├── analytics_agent.py
│   │   ├── knowledge_retriever.py
│   │   ├── multimodal_assistant.py
│   │   ├── reasoning_agent.py
│   │   └── speech_tools.py
│   │   └── vision_tools.py
│   ├── tools/              # MCP 工具函式
│   ├── config.py
│   └── llm_client.py       # Gemini / OpenRouter API Wrapper
├── data/                   # MCP 說明文檔、向量化資料
├── frontend/               # Streamlit UI (optional)
├── docker-compose.yml
├── requirements.txt
└── README.md


```
```
           [使用者]
         /    |     \
     語音   文字    圖像
      ↓      ↓        ↓
[語音轉文字] [文字處理] [影像分析]
       \     |      /
        \    ↓     /
          [主 AI 助理 Agent (LLM)]
            /     |       \
     [知識查詢] [意圖解析] [MCP指令生成]
        ↓         ↓             ↓
 [RAG Agent]  [Tool Agent]    [MCP Control Agent]
       ↓                         ↓
 [Qdrant+Embedding]      [MCP Server / Websocket]

```

