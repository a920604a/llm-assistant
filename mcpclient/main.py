from api.routers import dashboard, query, setting
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logger import get_logger
from prometheus_fastapi_instrumentator import Instrumentator

logger = get_logger(__name__)


app = FastAPI(title="MCP Client Service")

Instrumentator().instrument(app).expose(app)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 先允許所有,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, tags=["query"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(setting.router, tags=["setting"])
