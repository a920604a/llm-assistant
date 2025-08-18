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
    %% === 前端模組 ===
    subgraph Frontend[前端]
        style Frontend fill:#FFD966,stroke:#333,stroke-width:2px
        U[使用者輸入 Query]
        style U fill:#FFF2CC,stroke:#333,stroke-width:1px
    end

    %% === Host 模組 ===
    subgraph Host[MCP Host + Ollama]
        style Host fill:#9FC5E8,stroke:#333,stroke-width:2px
        G[生成 Generation]
        HR[重排 Re-ranking, 多來源]
        style G fill:#D9E1F2,stroke:#333,stroke-width:1px
        style HR fill:#D9E1F2,stroke:#333,stroke-width:1px
    end

    %% === Note MCP Server ===
    subgraph NoteServer[Note MCP Server]
        style NoteServer fill:#F4CCCC,stroke:#333,stroke-width:2px
        C[分片 Chunking]
        I[索引 Indexing]
        R[召回 Retrieval]
        NR[重排 Re-ranking, 單來源]
        style C fill:#FCE5CD,stroke:#333,stroke-width:1px
        style I fill:#FCE5CD,stroke:#333,stroke-width:1px
        style R fill:#FCE5CD,stroke:#333,stroke-width:1px
        style NR fill:#FCE5CD,stroke:#333,stroke-width:1px
    end

    %% === Image Server ===
    subgraph ImageServer[Image MCP Server]
        style ImageServer fill:#C9DAF8,stroke:#333,stroke-width:2px
        Img[影像處理/分析]
        style Img fill:#D9E1F2,stroke:#333,stroke-width:1px
    end

    %% === Speech Server ===
    subgraph SpeechServer[Speech MCP Server]
        style SpeechServer fill:#D9EAD3,stroke:#333,stroke-width:2px
        Sp[語音處理/ASR/TTS]
        style Sp fill:#E2EFDA,stroke:#333,stroke-width:1px
    end

    %% === 流程連線 ===
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
