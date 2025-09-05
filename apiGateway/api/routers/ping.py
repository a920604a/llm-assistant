from api.auto_metrics import observe_api
from api.schemas.health import HealthResponse, ServiceStatus
from config import SettingsDep
from core.limiter import limiter
from fastapi import APIRouter, Request
from services.ollama_client import OllamaClient
from sqlalchemy import text
from storage import db_session

router = APIRouter()


@router.get("/api/ping")
@limiter.limit("20/minute")  # 每分鐘 20 次
@observe_api
async def ping(request: Request):
    """Simple ping endpoint for basic connectivity tests."""
    return {"status": "ok", "message": "pong"}


@router.get("/api/health", response_model=HealthResponse)
@limiter.limit("20/minute")  # 每分鐘 20 次
@observe_api
async def health_check(request: Request, settings: SettingsDep) -> HealthResponse:
    """Comprehensive health check endpoint for monitoring and load balancer probes.

    :returns: Service health status with version and connectivity checks
    :rtype: HealthResponse
    """
    services = {}
    overall_status = "ok"

    def _check_service(name: str, check_func, *args, **kwargs):
        """Helper to standardize service health checks."""
        try:
            if kwargs.get("is_async"):
                # Handle async functions separately in the calling code
                return check_func(*args)
            result = check_func(*args)
            services[name] = result
            if result.status != "healthy":
                nonlocal overall_status
                overall_status = "degraded"
        except Exception as e:
            services[name] = ServiceStatus(status="unhealthy", message=str(e))
            overall_status = "degraded"

    # Database check
    def _check_database():
        with db_session() as db:
            db.execute(text("SELECT 1"))
        return ServiceStatus(status="healthy", message="Connected successfully")

    # Run synchronous checks
    _check_service("database", _check_database)

    # Handle Ollama async check separately
    try:
        ollama_client = OllamaClient()
        ollama_health = await ollama_client.health_check()
        services["ollama"] = ServiceStatus(
            status=ollama_health["status"], message=ollama_health["message"]
        )
        if ollama_health["status"] != "healthy":
            overall_status = "degraded"
    except Exception as e:
        services["ollama"] = ServiceStatus(status="unhealthy", message=str(e))
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        service_name=settings.service_name,
        services=services,
    )
