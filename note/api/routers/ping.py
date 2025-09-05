from api.auto_metrics import observe_api
from api.schemas.health import HealthResponse, ServiceStatus
from botocore.exceptions import ClientError
from config import SettingsDep
from fastapi import APIRouter, Request
from qdrant_client.http.exceptions import UnexpectedResponse
from services.ollama_client import OllamaClient
from sqlalchemy import text
from storage import db_session
from storage.minio import s3_client
from storage.qdrant import qdrant_client

router = APIRouter()


@router.get("/api/ping")
@observe_api
async def ping(request: Request):
    """Simple ping endpoint for basic connectivity tests."""
    return {"status": "ok", "message": "pong"}


@router.get("/api/health", response_model=HealthResponse)
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

    def _check_qdrant():
        try:
            collections = qdrant_client.get_collections()
            col_names = [c.name for c in collections.collections]
            if settings.COLLECTION_NAME in col_names:
                return ServiceStatus(status="healthy", message="Qdrant reachable")
            else:
                return ServiceStatus(
                    status="unhealthy",
                    message=f"Collection `{settings.COLLECTION_NAME}` not found",
                )
        except UnexpectedResponse as e:
            return ServiceStatus(status="unhealthy", message=str(e))

    def _check_minio():
        try:
            buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
            if settings.MINIO_BUCKET in buckets:
                return ServiceStatus(status="healthy", message="MinIO reachable")
            else:
                return ServiceStatus(
                    status="unhealthy",
                    message=f"Bucket `{settings.MINIO_BUCKET}` not found",
                )
        except ClientError as e:
            return ServiceStatus(status="unhealthy", message=str(e))

    # Run synchronous checks
    _check_service("database", _check_database)
    _check_service("minio", _check_minio)
    _check_service("qdrant", _check_qdrant)

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
