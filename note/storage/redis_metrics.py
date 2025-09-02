# Redis metrics
import time

from prometheus_client import Counter, Histogram

REDIS_GET_COUNT = Counter("redis_get_total", "Total Redis GET requests")
REDIS_SET_COUNT = Counter("redis_set_total", "Total Redis SET requests")
REDIS_LATENCY = Histogram("redis_latency_seconds", "Redis operation latency")
REDIS_ERROR = Counter("redis_error_total", "Redis operation errors")


def monitored_redis(func):
    """Redis decorator"""

    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            # 判斷是 GET 還是 SET
            if func.__name__.startswith("get"):
                REDIS_GET_COUNT.inc()
            else:
                REDIS_SET_COUNT.inc()
            return result
        except Exception:
            REDIS_ERROR.inc()
            raise
        finally:
            REDIS_LATENCY.observe(time.time() - start)

    return wrapper
