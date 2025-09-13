import os
from contextlib import asynccontextmanager

from api.routers import chat_history, ping, setting, user
from api.routers.ask import ask_router, stream_router
from config import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logger import AppLogger
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from services.cache.factory import make_all_cache_clients
from services.langchain.factory import make_langchain_client
from services.langfuse.factory import make_langfuse_tracer
from services.minio.factory import make_minio_client
from services.ollama.factory import make_ollama_client
from services.qdrant.factory import make_qdrant_client
from starlette.concurrency import run_in_threadpool

logger = AppLogger(__name__).get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the API.
    # 啟動前
    yield
    # 關閉前

    """
    logger.info("Starting RAG API...")

    settings = get_settings()
    app.state.settings = settings

    # Initialize search service
    qdrant_client = make_qdrant_client()
    app.state.qdrant_client = qdrant_client

    # Initialize other services (kept for future endpoints and notebook demos)
    # app.state.arxiv_client = make_arxiv_client()
    # app.state.pdf_parser = make_pdf_parser_service()
    # app.state.embeddings_service = make_embeddings_service()
    app.state.minio_client = make_minio_client()
    app.state.ollama_client = make_ollama_client()
    app.state.langchain_client = make_langchain_client()
    app.state.langfuse_tracer = make_langfuse_tracer()
    _clients = make_all_cache_clients()
    app.state.cache_user_client = _clients["user"]
    app.state.cache_paper_client = _clients["paper"]

    logger.info("🚀 startup_event triggered")
    await run_in_threadpool(app.state.langchain_client.create_note_collection)
    logger.info("✅ note_collection ready")
    await run_in_threadpool(app.state.minio_client.create_note_bucket)
    logger.info("✅ note_bucket ready")

    logger.info("API ready")
    yield

    # Cleanup
    logger.info("API shutdown complete")


app = FastAPI(
    title="Note for arXiv Paper",
    description="Personal arXiv CS.AI paper curator with RAG capabilities",
    version=os.getenv("APP_VERSION", "0.1.0"),
    lifespan=lifespan,
)


Instrumentator().instrument(app).expose(app)

origins = ["http://apiGateway:8000"]


# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = (
    Instrumentator()
    .add(
        metrics.default(
            metric_namespace="llm_assistance",  # Don't user -
            metric_subsystem="noteservice",
            custom_labels={"environment": "noteservice"},
        )
    )
    .instrument(app)
    .expose(app)
)


# REST API routers

app.include_router(ask_router)  # RAG question answering with LLM
app.include_router(stream_router)  # Streaming RAG responses

app.include_router(user.router, tags=["user"])
app.include_router(setting.router, tags=["setting"])
app.include_router(chat_history.router, tags=["chat_history"])
app.include_router(ping.router, tags=["Health"])
