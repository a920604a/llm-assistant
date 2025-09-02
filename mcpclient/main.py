from api.routers import dashboard, query, setting
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logger import AppLogger

# from prometheus_fastapi_instrumentator import Instrumentator, metrics
#
from prometheus_fastapi_instrumentator import Instrumentator, metrics

logger = AppLogger(__name__).get_logger()


app = FastAPI(title="MCP Client Service")

# Instrumentator().instrument(app).expose(app)
instrumentator = (
    Instrumentator()
    .add(
        metrics.default(
            metric_namespace="llm_assistance",  # Don't user -
            metric_subsystem="llm_assistance",
            custom_labels={"environment": "mcpclient"},
        )
    )
    .instrument(app)
    .expose(app)
)

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
