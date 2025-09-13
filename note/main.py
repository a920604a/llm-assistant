from api.routers import chat_history, ping, setting, user
from api.routers.ask import ask_router, stream_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logger import AppLogger
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from starlette.concurrency import run_in_threadpool
from storage.minio import create_note_bucket
from storage.qdrant import create_qdrant_collection as create_note_collection

logger = AppLogger(__name__).get_logger()


app = FastAPI(title="Note Server")
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


# Startup event: 確保 Qdrant 啟動後再建立 collection
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 startup_event triggered")
    await run_in_threadpool(create_note_collection)
    logger.info("✅ note_collection ready")
    await run_in_threadpool(create_note_bucket)
    logger.info("✅ note_bucket ready")
