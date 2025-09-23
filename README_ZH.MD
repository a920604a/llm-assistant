
# Arxiv Knowledge Assistant (Beta)

[英文版](README.MD)


## Objective

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

## 📦 Quick Start

```shell
git clone https://github.com/a920604a/llm-assistant.git
cd llm-assistant
cp .env.example .env
make build && make up

```

Frontend: `make up-front` → http://localhost:5173

Gradio UI (optional): `cd gradio && python app.py` → http://localhost:7861

Monitoring: `http://localhost:3002` (Grafana)


---

## Requirements
- Docker & Docker Compose

---
## 🖥️ System Architecture



1. The system ingests daily arXiv papers → stores PDFs/metadata → builds embeddings in Qdrant
2. RAG pipeline retrieves + re-ranks → answers delivered to frontend dashboard
3. email subscriptions , fetch paper in qdrant → generate summary → send email

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

## 🚀 Technologies Used

| 類別                | 工具與框架                                            |
| ----------------- | ------------------------------------------------ |
| **Cloud / Infra** | Docker Compose、MinIO、PostgreSQL、Qdrant           |
| **Backend / API** | FastAPI, Celery, Prefect 2                       |
| **Frontend**      | React + Vite  and gradio                                   |
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
├── apiGateway/               # API Gateway backend service
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




## 🔁 Reproducibility

為了確保專案能完整重現，請建立一份 **`.env`** 檔案，並填入以下環境變數。

使用者需自行準備 **Firebase Service Account Key**：

1. 前往 [Firebase Console](https://console.firebase.google.com/) 建立專案
2. 啟用 **Authentication**（Google 登入）
3. 建立 Service Account 並下載 `serviceAccountKey.json`
4. 放置於 `apiGateway/serviceAccountKey.json` `email/serviceAccountKey.json`

> 若未提供 Key，系統將無法驗證使用者，也無法存取 Firebase 資料。

### React Frontend interface
> 若未提供 Key，系統將無法驗證使用者，也無法存取 Firebase 資料。

```shell
make up-front
```
visited `http://localhost:5173/`

### Gradio
如果你不想申請 firebase ，可以選擇這個前端。
![](demo/gradio.png)

```shell
pip install gradio
cd gradio
python app.py
```


### Database & Cache

```bash
DATABASE_URL=postgresql://user:password@note-db:5432/note

REDIS_URL=redis://redis:6379/2                # Note server
REDIS_AUTH=REDIS_AUTH
```

### Object Storage (MinIO)

```bash
MINIO__ENDPOINT=http://note-minio:9000
MINIO__ACCESS_KEY=MINIO__ACCESS_KEY
MINIO__SECRET_KEY=MINIO__SECRET_KEY
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


## 📈 Checklist

| Item                 | Notes                                                                      |
| -------------------- | -------------------------------------------------------------------------- |
| Problem description  | Clear functionality and objectives                                         |
| Retrieval flow       | [RAG + LLM Q&A flow](docs/rag_chat.md) and [code: retrieval_pipeline method](note/arxiv_rag_pipeline.py)             |
| Retrieval evaluation | [Initial tests, not yet optimized](note/services/evaluate.py) |
| LLM evaluation       | Supports multiple prompt templates                                         |
| Interface            | [React Web](http://localhost)   or [arXiv Paper Assistance - RAG Chat]     |
| Ingestion pipeline   | [daily arXiv pipeline](arxiv/arxiv_pipeline.py)             |
| Monitoring           | [Grafana](http://localhost:3002)    or      ![](demo/app_metrics.png)    |
| Containerization     | [Full Docker Compose setup](docker-compose.dev.yml)                        |
| Reproducibility      | Complete setup + requirements, Firebase key required                       |
| Hybrid search        | [search](note/services/qdrant/client.py)                            |
| Document re-ranking  | [re_ranking method](note/services/rerank.py)                               |
| User query rewriting | [rewrite_query method](note/services/langchain/client.py)                                  |


---

## 📦 Installation Guide

```bash
make up

```

---

---


## 🎥 Demo
![](demo/homepage.png)
![](demo/gradio.png)
![](demo/app_metrics.png)

![](demo/demo.mp4)

---


## 🛠️ Roadmap
- [ ] GitHub Actions CI/CD
- [ ] Unit & integration testing
- [ ] Multi-LLM backend (OpenAI, Anthropic, etc.)
- [ ] Personalized recommendation / subscription

---


## 🔗 Useful Resources

* [Firebase Authentication](https://firebase.google.com/docs/auth)
* [Qdrant](https://qdrant.tech/documentation/)
* [Prefect 3](https://docs.prefect.io/)
* [Grafana](https://grafana.com/)
* [Langfuse](https://langfuse.com/)

---

## 📜 License

MIT License

Thank you to arXiv for use of its open access interoperability.
