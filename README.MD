# Arxiv Knowledge Assistant

[中文版](README_ZH.MD)


## Objective

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

| Category          | Tools & Frameworks                                       |
| ----------------- | -------------------------------------------------------- |
| **Cloud / Infra** | Docker Compose, MinIO, PostgreSQL, Qdrant                |
| **Backend / API** | FastAPI, Prefect 2                                       |
| **Frontend**      | React + Vite  and gradio                                   |
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
├── apiGateway/               # API Gateway backend service
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

## 🔁 Reproducibility

To reproduce the environment, create a **`.env`** file and set the required environment variables.

You must prepare a **Firebase Service Account Key**:

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a project
2. Enable **Authentication** (Google Login)
3. Create a Service Account and download `serviceAccountKey.json`
4. Place it in `apiGateway/serviceAccountKey.json` and `email/serviceAccountKey.json`

> Without the key, user authentication and Firebase access will not work.


### React Frontend interface
> Without the key, user authentication and Firebase access will not work.
![](demo/homepage.png)

```shell
make up-front
```
visited `http://localhost:5173/`

### Gradio
If you want to apply Firebase project, you would choose this solution as your interface
![](demo/gradio.png)

```shell
pip install gradio
cd gradio
python app.py
```

efault: `http://localhost:7861`

### Database & Cache

```bash
DATABASE_URL=postgresql://user:password@note-db:5432/note

REDIS_URL=redis://redis:6379/2
REDIS_AUTH=REDIS_AUTH
```

### Object Storage (MinIO)

```bash
MINIO__ENDPOINT=http://note-minio:9000
MINIO_ACCESS_KEY=MINIO_ACCESS_KEY
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
2. Run `make net-create && make up`
3. You should be able to reproduce the same environment 🎯

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
