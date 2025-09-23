from contextlib import asynccontextmanager

from api.routers import chat_history, dashboard, ping, query, setting
from config import get_settings
from core.middleware import setup_middlewares
from fastapi import FastAPI
from logger import AppLogger
from services.langchain.factory import make_langchain_client
from services.ollama.factory import make_ollama_client

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

    app.state.ollama_client = make_ollama_client()

    app.state.langchain_client = make_langchain_client()

    logger.info("API ready")
    yield

    # Cleanup
    logger.info("API shutdown complete")


app = FastAPI(
    title="API Getway Service",
    description=" Getway Service offer auth",
    lifespan=lifespan,
)


# === 設定中間件 ===
setup_middlewares(app)


app.include_router(query.router, tags=["query"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(setting.router, tags=["setting"])
app.include_router(chat_history.router, tags=["chat_history"])
app.include_router(ping.router, tags=["Health"])
