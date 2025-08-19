```
arxiv_ingestion/
├── arxiv_pipeline.py          # Main pipeline for fetching, processing, and storing ArXiv papers
├── arxiv_rag_pipeline.py      # RAG pipeline for retrieval-augmented generation using LLM
├── config.py                  # Configuration settings (e.g., API URLs, collection names)
├── db/
│   ├── factory.py             # Database session/factory creation
│   ├── minio.py               # MinIO client setup for PDF storage
│   ├── models.py              # ORM models for database entities (Paper, User, etc.)
│   └── qdrant.py              # Qdrant client setup and utilities for vector DB
├── exceptions.py              # Custom exception classes
├── flows/
│   └── daily_flow.py          # Prefect daily scheduled flow orchestration
├── readme.md                  # Project overview and instructions
├── services/
│   ├── arxiv_client.py        # Client for querying ArXiv API
│   ├── embedding.py           # Embedding functions for text to vector
│   ├── metadata_fetcher.py    # Extracting metadata from ArXiv papers
│   ├── pdf_parser.py          # Parsing PDFs to extract text or sections
│   └── schemas.py             # Pydantic schemas / data models
└── tasks/
    ├── fetch_papers.py        # Prefect task to fetch papers from ArXiv
    ├── generate_report.py     # Task to generate summary reports
    ├── llm.py                 # Task for calling LLM (Ollama) for text generation
    ├── process_pdfs.py        # Task to parse PDFs and extract content
    ├── prompt.py              # Task to build prompts for LLM
    ├── qdrant_index.py        # Task to index paper chunks into Qdrant
    ├── rerank.py              # Task to rerank retrieved chunks (vector + text)
    ├── retrieval.py           # Task to retrieve relevant chunks from Qdrant
    └── store_papers.py        # Task to store processed papers into DB

```

- 感謝 arXiv 提供其開放存取服務
- 每次請求間隔 ≥ 3 秒，僅一連線
- 每分鐘最多 1 個 request



```mermaid
flowchart TD
    %% === Ingestion Pipeline ===
    subgraph Ingest_Arxiv["Arxiv Paper Ingestion Pipeline"]
        A1[Fetch Papers]
        A2[Process PDFs <br> leverage metadata ]
        A3[Qdrant Index Task<br> Chunking policy]
        A4[Store Papers Task<br> DB storage]
        A5[Generate Report Task]

        A1 --> A2
        A2 --> A3
        A3 --> A4
        A4 --> A5
    end

    %% === RAG Search Pipeline ===
    subgraph RAG_Pipeline["Arxiv Paper RAG Pipeline"]
        B1[ Query Rewrite Task @ MCP Client ]
        B2[Retrieval Task<br> Search]
        B3[Document Reranking Task]
        B4[Build Prompt Task]
        B5[LLM Generation Task]

        B1 --> B2
        B2 --> B3
        B3 --> B4
        B4 --> B5
    end

    %% === Optional Connection ===
    A3 -->|Indexed chunks| B2

A2 --> |storage| MinIO
A2 --> |storage| Local["local storage"]
A3 --> |indexing| Qdrant
A4 --> |storage| DB

Qdrant --> |Fetch| B2
B1 <--> LLM
B5 <--> LLM

```