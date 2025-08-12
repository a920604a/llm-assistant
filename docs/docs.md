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



- Agendic RAG
- reAct
- self-RAG

```mermaid
flowchart LR
    subgraph Frontend[前端]
        U[使用者輸入 Query]
    end

    subgraph Host[MCP Host + Ollama]
        G[生成 Generation]
        HR[重排 Re-ranking, 多來源]
    end

    subgraph NoteServer[Note MCP Server]
        C[分片 Chunking]
        I[索引 Indexing]
        R[召回 Retrieval]
        NR[重排 Re-ranking, 單來源]
    end

    subgraph ImageServer[Image MCP Server]
        Img[影像處理/分析]
    end

    subgraph SpeechServer[Speech MCP Server]
        Sp[語音處理/ASR/TTS]
    end

    U --> |Query| Host
    Host --> |傳送 Query| NoteServer
    NoteServer --> C --> I
    I --> |建立向量索引| R
    R --> NR
    NR --> |Top-K chunks| Host
    Host --> HR
    ImageServer --> HR
    SpeechServer --> HR
    HR --> G
    G --> |最終回答| U

```