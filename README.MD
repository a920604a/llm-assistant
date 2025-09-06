# Arxiv Knowledge Assistant (Beta)

[英文版](README_ZH.MD)

## 🎯 Course Project

### Objective

This project aims to build an **arXiv knowledge retrieval platform**, implementing a complete pipeline of data ingestion, vector-based retrieval, LLM-powered Q\&A, and a visualization dashboard.

Users can query paper abstracts, PDFs, Q\&A history, and references. Developers can configure ingestion pipelines, manage vector indexes, monitor model performance, and extend the system to personalized RAG strategies or subscription services.

---

## 🧩 Problem Statement

* Automatically fetch daily arXiv papers: Metadata, PDFs, and abstracts
* Support bilingual translation (Chinese/English) and Q\&A
* Provide vector database retrieval + LLM-based Q\&A (RAG)
* Customizable prompt templates
* Dashboard for viewing query history
* Email push subscription
* Future work: CI/CD, unit & integration testing

---

## 🚀 Technologies Used

| Category          | Tools & Frameworks                                       |
| ----------------- | -------------------------------------------------------- |
| **Cloud / Infra** | Docker Compose, MinIO, PostgreSQL, Qdrant                |
| **Backend / API** | FastAPI, Celery, Prefect 2                               |
| **Frontend**      | React + Vite                                             |
| **Monitoring**    | Prometheus + Grafana, Logging                            |
| **CI/CD**         | GitHub Actions (planned)                                 |
| **Testing**       | pytest (unit + integration, WIP)                         |
| **IaC**           | Docker Compose + Volumes + Networks (Terraform optional) |

---

## 🏗️ Project Structure

```
.
├── frontend/                 # React Vite app
├── data/, database/          # Database & storage initialization
├── docs/                     # Documentation & implementation notes
├── apiGateway/               # MCP Client backend service
├── image/                    # Image-related scripts (future extension)
├── speech/                   # Speech backend service (future extension)
├── arxiv/                    # Arxiv ingestion service
├── email/                    # Email subscription service
├── note/                     # Note backend service (RAG tasks)
├── ollama_models/            # Local Ollama model management
├── services/                 # Microservices Dockerfiles & requirements
│   ├── arxivservice/
│   ├── emailservice/
│   ├── imageservice/
│   ├── apiGateway/
│   ├── noteservice/
│   └── speechservice/
├── terraform/                # Optional IaC scripts
├── docker-compose*.yml       # Docker Compose configs
├── Dockerfile.*              # Individual service Dockerfiles
├── Makefile, setup.sh, requirements.txt
├── package-lock.json
├── terraform.tfstate
├── test/                     # Unit & integration tests
└── README.md
```

---

## 🧪 System Workflow

1. Celery Beat schedules daily arXiv ingestion
2. PDFs and metadata are stored in MinIO / PostgreSQL
3. Text embeddings stored in Qdrant
4. Q\&A uses RAG + agent reflection strategy
5. Results are returned to the frontend dashboard
6. CI/CD and model updates can later be automated via GitHub Actions

---

## 🖥️ System Architecture (Mermaid)

```mermaid
flowchart TB
User[User]:::user --> Nginx[Nginx / API Gateway]:::frontend
Nginx --> Client[Web UI / Frontend]:::frontend

subgraph API[API & Services]
  FastAPI[Client API for auth]:::api
  NoteServer[RAG Service]:::service
end

Client --> FastAPI
FastAPI --> NoteServer

subgraph Storage[Storage]
  MinIO[(MinIO : PDFs)]:::storage
  PostgreSQL[(PostgreSQL : Metadata / Chats)]:::storage
  Qdrant[(Qdrant : Vectors)]:::storage
end

NoteServer --> MinIO
NoteServer --> PostgreSQL
NoteServer --> Qdrant
FastAPI    --> LLM
NoteServer --> LLM

subgraph LLM[LLM Engines]
  Ollama[Ollama]:::llm
end

subgraph Ingest[Ingestion Pipeline]
  Scheduler[Daily Schedule]:::scheduler
  IngestFlow[Fetch + Parse + Chunk + Embed + Index]:::pipeline1
end

subgraph Data[DataSource]
Arxiv
end
Arxiv --> IngestFlow
Scheduler --> IngestFlow
IngestFlow --> MinIO
IngestFlow --> PostgreSQL
IngestFlow --> Qdrant

subgraph Subscription[Email Subscription Pipeline]
  SubSched[Daily Schedule]:::scheduler
  SubFlow[User Filter → Fetch Paper → Summarize → Send]:::pipeline2
end

SubSched --> SubFlow
Storage --> SubFlow
SubFlow --> User

subgraph Worker[Workers & Queue]
  Queue1[Notes Queue]:::queue
  Queue2[Email Queue]:::queue
end

Scheduler --> Queue1
SubSched --> Queue2
Queue1 --> IngestFlow
Queue2 --> SubFlow

classDef user fill:#FFD700,stroke:#333,stroke-width:1px
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

To reproduce the environment, create a **`.env`** file and set the required environment variables.

You must prepare a **Firebase Service Account Key**:

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a project
2. Enable **Authentication** (Google Login)
3. Create a Service Account and download `serviceAccountKey.json`
4. Place it in `apiGateway/serviceAccountKey.json` and `email/serviceAccountKey.json`

> Without the key, user authentication and Firebase access will not work.

### Database & Cache

```bash
DATABASE_URL=postgresql://user:password@note-db:5432/note

REDIS_URL=redis://redis:6379/2
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
REDIS_BACKEND=redis://redis:6379/3
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
MAIL_USERNAME=example@gmail.com
MAIL_PASSWORD=xxxxxx
MAIL_FROM=example@gmail.com
```

> ⚠️ Use [Google App Passwords](https://myaccount.google.com/apppasswords) for `MAIL_PASSWORD` and `SMTP_AUTH_PASSWORD`.

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
ALERT_EMAIL_TO=example@gmail.com
ALERT_RESOLVE_TIMEOUT=5m
SMTP_SMARTHOST=smtp.gmail.com:587
SMTP_FROM=example@gmail.com
SMTP_AUTH_USERNAME=example@gmail.com
SMTP_AUTH_PASSWORD=xxxxxx
SMTP_REQUIRE_TLS=true
```

Steps:

1. Copy `.env.example` → `.env`, and fill in your credentials
2. Run `make up` or `docker-compose up`
3. You should be able to reproduce the same environment 🎯

---

## 📈 Checklist

| Item                 | Notes                                                                      |
| -------------------- | -------------------------------------------------------------------------- |
| Problem description  | Clear functionality and objectives                                         |
| Retrieval flow       | [RAG + LLM Q\&A flow](docs/rag_chat.md)                                    |
| Retrieval evaluation | [Initial tests, not yet optimized](note/arxiv_ingestion/tasks/evaluate.py) |
| LLM evaluation       | Supports multiple prompt templates                                         |
| Interface            | [Web UI + Dashboard](http://localhost)                                     |
| Ingestion pipeline   | [Celery Beat daily arXiv fetch](arxiv/flows/arxiv_pipeline.py)             |
| Monitoring           | [Grafana](http://localhost:3002)                                           |
| Containerization     | [Full Docker Compose setup](docker-compose.dev.yml)                        |
| Reproducibility      | Complete setup + requirements, Firebase key required                       |
| Hybrid search        | [here](note/arxiv_ingestion/tasks/retrieval.py)                            |
| Document re-ranking  | [here](note/arxiv_ingestion/tasks/rerank.py)                               |
| User query rewriting | [here](note/services/langchain_client.py)                                  |

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
