
# Arxiv Knowledge Assistant (Beta)

[英文版](README.MD)

## 🎯 Course Project

### Objective

本專案旨在建構一個 **arXiv 論文知識檢索平台**，實作完整的資料擷取、向量化檢索、LLM 問答與可視化 Dashboard。

使用者可以查詢論文摘要、PDF、問答紀錄與引用來源；開發者可設定自動擷取流程、管理向量索引、觀察模型回答效能，並可擴充至個人化 RAG 策略、服務訂閱。

---

## 🧩 Problem Statement

* 自動抓取每日 arXiv 論文：Metadata、PDF、摘要
* 支援中英文翻譯與問答
* 提供向量資料庫檢索 + LLM 問答（RAG）
* 可客製化 Prompt
* Dashboard 查看歷史紀錄
* Email 推送
* 未來計畫：、CICD、單元/整合測試

---

## 🚀 Technologies Used

| 類別                | 工具與框架                                            |
| ----------------- | ------------------------------------------------ |
| **Cloud / Infra** | Docker Compose、MinIO、PostgreSQL、Qdrant           |
| **Backend / API** | FastAPI, Celery, Prefect 2                       |
| **Frontend**      | React + Vite                                     |
| **Monitoring**    | Prometheus + Grafana, Logging                    |
| **CI/CD**         | GitHub Actions (未完成)                             |
| **Testing**       | pytest（單元 + 整合，尚未完成）                             |
| **IaC**           | Docker Compose + Volume + Network（可延伸 Terraform） |

---

## 🏗️ Project Structure

```
.
.
├── frontend/                 # React Vite app
├── data/, database/          # Database & storage initialization
├── docs/                     # 技術文件、實作歷程
├── apiGateway/                # MCP Client backend service
├── image/                    # Image-related scripts (未來擴充)
├── speech/                   # Speech service backend (未來擴充)
├── arxiv/                    # Arxiv service (Arxiv ingestion)
├── email/                    # email subscription service (email subscriptionubs)
├── note/                     # Note backend service (RAG tasks)
├── ollama_models/            # 本地 Ollama 模型管理
├── services/                 # 各微服務 Dockerfile & requirements
│   ├── arxivservice/
│   ├── emailservice/
│   ├── imageservice/
│   ├── apiGateway/
│   ├── noteservice/
│   └── speechservice/
├── terraform/                # 可選 IaC 腳本
├── docker-compose*.yml       # Docker Compose configurations
├── Dockerfile.*              # 各容器 Dockerfile
├── Makefile, setup.sh, require.txt
├── package-lock.json
├── terraform.tfstate
├── test/                     # 單元測試 & Pytest
└── README.md

```

---

## 🧪 System Workflow

1. Celery Beat 定期觸發 arXiv 擷取流程
2. PDF 與 Metadata 儲存至 MinIO / PostgreSQL
3. 文本向量化存入 Qdrant
4. LLM 問答使用 RAG + Agent 反思策略
5. 結果回傳至前端 Dashboard
6. 日後可透過 GitHub Actions 觸發 CICD / 模型更新

---

## 🖥️ System Architecture (Mermaid)


```mermaid
flowchart LR

subgraph Data[DataSource]
  Arxiv
end


Arxiv --> Ingest


subgraph Ingest[Data Ingestion Pipeline]
  Scheduler[Daily Schedule]:::scheduler
  IngestFlow[Fetch + Parse + Chunk + Embed + Index]:::pipeline1
end


subgraph API[API Layer]
  FastAPI[Client API for auth]:::api
  NoteServer[RAG Service]:::service
end

Client --> FastAPI
FastAPI --> NoteServer

Storage e3@ --> Retrieve
subgraph Retrieve[Retrieve pipeline]
    Search[Hybrid Search ] --> Rerank
    Rerank --> prompt
end

prompt e4@ --> LLM

subgraph LLM[LLM Engines]
  Ollama[Ollama]:::llm
end

subgraph Storage[Storage]
  MinIO[(MinIO : PDFs)]:::storage
  PostgreSQL[(PostgreSQL : Metadata / )]:::storage
  Qdrant[(Qdrant : Vectors)]:::storage
end

NoteServer e5@ --> Retrieve
LLM --> API



Scheduler --> IngestFlow
IngestFlow e1@ --> Storage


subgraph Subscription[Email Subscription Pipeline]
    direction LR
  SubSched[Daily Schedule]:::scheduler
  SubFlow[Filter → Fetch Paper → Summarize → Send]:::pipeline2
    SubSched --> SubFlow
end

Storage e2@ --> Subscription 

e1@{ animation: slow }
e2@{ animation: slow }
e3@{ animation: fast }
e4@{ animation: fast }
e5@{ animation: fast }

classDef frontend fill:#87CEEB,stroke:#333,stroke-width:1px
classDef api fill:#FFA500,stroke:#333,stroke-width:1px
classDef service fill:#7FFFD4,stroke:#333,stroke-width:1px
classDef storage fill:#F08080,stroke:#333,stroke-width:1px
classDef pipeline1 fill:#9370DB,stroke:#333,stroke-width:1px
classDef pipeline2 fill:#40E0D0,stroke:#333,stroke-width:1px
classDef scheduler fill:#BA55D3,stroke:#333,stroke-width:1px
classDef llm fill:#90EE90,stroke:#333,stroke-width:1px
classDef queue fill:#D2691E,stroke:#333,stroke-width:1px
classDef data fill:#C0C0C0,stroke:#333,stroke-width:1px




```



---

## 🔁 Reproducibility

為了確保專案能完整重現，請建立一份 **`.env`** 檔案，並填入以下環境變數。

使用者需自行準備 **Firebase Service Account Key**：

1. 前往 [Firebase Console](https://console.firebase.google.com/) 建立專案
2. 啟用 **Authentication**（Google 登入）
3. 建立 Service Account 並下載 `serviceAccountKey.json`
4. 放置於 `apiGateway/serviceAccountKey.json` `email/serviceAccountKey.json`

> 若未提供 Key，系統將無法驗證使用者，也無法存取 Firebase 資料。

### Database & Cache

```bash
DATABASE_URL=postgresql://user:password@note-db:5432/note

REDIS_URL=redis://redis:6379/2                # Note server
CELERY_BROKER_URL=redis://redis:6379/0        # Note Celery broker
CELERY_RESULT_BACKEND=redis://redis:6379/1    # Note Celery result backend
REDIS_BACKEND=redis://redis:6379/3            # 其他 Redis backend
REDIS_AUTH=REDIS_AUTH
```

### Object Storage (MinIO)

```bash
MINIO_ENDPOINT=http://note-minio:9000
MINIO_ACCESS_KEY=MINIO_ACCESS_KEY
MINIO_SECRET_KEY=MINIO_SECRET_KEY
MINIO_BUCKET=note-md
```

### Vector DB & LLM

```bash
QDRANT_URL=http://note-qdrant:6333
OLLAMA_API_URL=http://ollama:11434
```

### Email Service

```bash
MAIL_USERNAME=qaaaaaa@gmail.com
MAIL_PASSWORD=qaaaaaadsfdfdf
MAIL_FROM=qaaaaaa@gmail.com
```

> ⚠️ 需至 [Google App Passwords](https://myaccount.google.com/apppasswords) 申請專屬應用程式密碼填入 `MAIL_PASSWORD` 與 `SMTP_AUTH_PASSWORD`。

### Langfuse

```bash
LANGFUSE_PUBLIC_KEY=LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY=LANGFUSE_SECRET_KEY
LANGFUSE_HOST=http://langfuse-web:3000

LANGFUSE_INIT_USER_EMAIL=admin@example.com
LANGFUSE_INIT_USER_NAME=LANGFUSE_INIT_USER_NAME
LANGFUSE_INIT_USER_PASSWORD=LANGFUSE_INIT_USER_PASSWORD
```

### Monitoring (Grafana & Alertmanager)

```bash
# Grafana
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin54321

# Alertmanager
ALERT_EMAIL_TO=qaaaaaadsfdfdf@gmail.com
ALERT_RESOLVE_TIMEOUT=5m
SMTP_SMARTHOST=smtp.gmail.com:587
SMTP_FROM=qaaaaaadsfdfdf@gmail.com
SMTP_AUTH_USERNAME=qaaaaaadsfdfdf@gmail.com
SMTP_AUTH_PASSWORD=qaaaaaadsfdfdf
SMTP_REQUIRE_TLS=true
```


1. 複製 `.env.example` → `.env`，填上自己的密鑰/帳密
2. `make net-create && make up`
3. 應該就能快速重現相同環境 🎯

---

## 📈  Checklist

| 項目                 | 備註                                         |
| -------------------- |  ------------------------------------------ |
| Problem description  |  功能與目標明確                                    |
| Retrieval flow       |  [RAG + LLM 問答流程](docs/rag_chat.md)                             |
| Retrieval evaluation |  [初步驗證，尚未最佳化](note/arxiv_ingestion/tasks/evaluate.py)  |
| LLM evaluation       |  支援多種 Prompt                     |
| Interface            |  [Web UI + Dashboard](http://localhost)                         |
| Ingestion pipeline   |  [Celery Beat 自動抓取 arXiv](arxiv/flows/arxiv_pipeline.py)|
| Monitoring           |  [grafana](http://localhost:3002)                   |
| Containerization     |  [Docker-compose 完整管理](docker-compose.dev.yml)                        |
| Reproducibility      |  完整 setup + requirements，Firebase Key 需自行提供 |
| Hybrid search        |  [here](note/arxiv_ingestion/tasks/retrieval.py)        |
| Document re-ranking  |  [here](note/arxiv_ingestion/tasks/rerank.py)         |
| User query rewriting |  [here](note/services/langchain_client.py) |

---

## 📦 Installation Guide

```bash
make up

```

---

## 🔗 Useful Resources

* [Firebase Authentication](https://firebase.google.com/docs/auth)
* [Qdrant](https://qdrant.tech/documentation/)
* [Prefect 2](https://docs.prefect.io/)
* [Grafana](https://grafana.com/)
* [Langfuse](https://langfuse.com/)

---

## 📜 License

MIT License
