import time

from core.limiter import limiter
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from logger import AppLogger
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from slowapi import _rate_limit_exceeded_handler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

logger = AppLogger(__name__).get_logger()


def setup_middlewares(app: FastAPI):
    # === Rate Limiter ===
    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)

    # === CORS ===
    origins = [
        "http://localhost",
        "http://localhost:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 指定 domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # === TrustedHost ===
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "mcpclient"],
    )

    # === Logging Middleware ===
    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start = time.time()
            response: Response = await call_next(request)
            duration = round(time.time() - start, 3)
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} ({duration}s)"
            )
            return response

    app.add_middleware(LoggingMiddleware)

    # === Prometheus Instrumentator ===
    _ = (
        Instrumentator()
        .add(
            metrics.default(
                metric_namespace="llm_assistance",
                metric_subsystem="mcpclient",
                custom_labels={"environment": "mcpclient"},
            )
        )
        .instrument(app)
        .expose(app)
    )

    return app
