```
.
├── celery_app.py                      # Celery configuration for task scheduling and background jobs
├── config.py                          # Configuration settings (API keys, DB connections, environment variables)
├── email_alarm_task.py                # Task definition for sending paper summary emails (entry point for alerts)
├── logger.py                          # Centralized logging utilities
├── pipeline.py                        # Main pipeline orchestrating the process of fetching, summarizing, and emailing papers
├── serviceAccountKey.json             # Firebase service account credentials for authentication
│
├── services/                          # Core services for fetching, processing, and delivering papers
│   ├── embedding.py                   # Functions for generating embeddings from paper text
│   ├── fetch_new_papers.py            # Fetch newly published papers from source (e.g., ArXiv API)
│   ├── fetch_paper_content.py         # Retrieve and parse the full content of papers
│   ├── filter_already_sent_papers.py  # Filter out papers that have already been sent to users
│   ├── generate_summary.py            # Generate summaries of papers using LLM
│   ├── get_subscribed_users.py        # Fetch the list of subscribed users from Firebase/DB
│   ├── get_user_email_from_firebase.py# Retrieve user email addresses from Firebase
│   ├── langchain_client.py            # Wrapper for interacting with LangChain (LLM interface)
│   ├── prompt_template.txt            # Prompt template used for LLM summarization
│   ├── record_sent_papers.py          # Log and persist which papers have been sent
│   ├── send_email.py                  # Utility to send emails with paper summaries to users
│   └── template.html                  # HTML template for summary emails
│
└── storage/                           # Storage and persistence layer
    ├── __init__.py                    # Package initialization
    ├── minio.py                       # MinIO client for storing PDFs or assets
    ├── model.py                       # ORM models or schema definitions for stored entities
    ├── qdrant_client.py               # Qdrant client for managing vector storage (embeddings, similarity search)
    ├── storage_metrics.py             # Metrics/logging for storage operations
    └── wait_minio.py                  # Utility to wait for MinIO service readiness before startup

```

### Layer-by-Layer Breakdown

**Pipeline Layer (`pipeline.py`, `email_alarm_task.py`)**

* Orchestrates the full workflow: fetching papers → summarizing → sending emails
* Defines task sequences and background job scheduling via Celery (`celery_app.py`)
* Handles alerting and scheduled dispatch of paper summaries

**Services Layer (`services/`)**

* Core business logic for paper retrieval, processing, summarization, and delivery
* Integration with external APIs: ArXiv for new papers, LangChain/LLM for summaries, Firebase for user info
* Handles filtering of already sent papers and ensures deduplication
* Embedding generation and vector similarity utilities (`embedding.py`)
* Email generation and formatting, including HTML templates (`template.html`)
* Error handling, retry mechanisms, and logging

**Storage Layer (`storage/`)**

* Persistence and storage management for PDFs, embeddings, and metadata
* MinIO client for asset storage (`minio.py`)
* Qdrant client for embedding storage and similarity search (`qdrant_client.py`)
* ORM models or schema definitions for persisted entities (`model.py`)
* Metrics collection and monitoring (`storage_metrics.py`)
* Utilities to ensure service readiness (e.g., `wait_minio.py`)

**Configuration & Utilities (`config.py`, `logger.py`, `serviceAccountKey.json`)**

* Centralized configuration for API keys, DB connections, and environment variables
* Logging utilities for structured and centralized logs
* Firebase credentials for user management and authentication
