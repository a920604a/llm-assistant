from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from api.routers import query, dashboard
from logger import get_logger

logger = get_logger(__name__)


app = FastAPI(title="MCP Client Service")

Instrumentator().instrument(app).expose(app)

origins = [
    "http://localhost",
    "http://localhost:5173",  # 如果前端跑在 5173 port
    # 其他允許的來源
]


# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, tags=["query"])
app.include_router(dashboard.router, tags=["dashboard"])
