import redis
from config import RedisSettings, get_settings
from logger import AppLogger
from services.cache.client import CacheClient

logger = AppLogger(__name__).get_logger()


def make_redis_client(redis_settings: RedisSettings) -> redis.Redis:
    """Create Redis client with connection pooling."""

    try:
        client = redis.from_url(
            redis_settings.url,  # e.g., redis://[:password]@host:port/db
            decode_responses=True,
            retry_on_timeout=True,
            retry_on_error=[redis.ConnectionError, redis.TimeoutError],
            socket_timeout=redis_settings.socket_timeout,
            socket_connect_timeout=redis_settings.socket_connect_timeout,
        )

        # Test connection
        client.ping()
        logger.info(f"Connected to Redis at {redis_settings.url}")
        return client

    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating Redis client: {e}")
        raise


def make_cache_client(settings: RedisSettings) -> CacheClient:
    """Create exact match cache client."""
    try:
        redis_client = make_redis_client(settings)
        cache_client = CacheClient(redis_client, settings)
        logger.info("Exact match cache client created successfully")
        return cache_client
    except Exception as e:
        logger.error(f"Failed to create cache client: {e}")
        raise


def make_all_cache_clients() -> dict[str, CacheClient]:
    settings = get_settings()
    return {
        "user": make_cache_client(settings.redis_user),
        "paper": make_cache_client(settings.redis_paper),
    }
