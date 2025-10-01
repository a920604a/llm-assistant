# Redis metrics
import time

from prometheus_client import Counter, Gauge, Histogram

REDIS_GET_COUNT = Counter("redis_get_total", "Total Redis GET requests")
REDIS_SET_COUNT = Counter("redis_set_total", "Total Redis SET requests")
REDIS_LATENCY = Histogram("redis_latency_seconds", "Redis operation latency")
REDIS_ERROR = Counter("redis_error_total", "Redis operation errors", ["error_type"])
REDIS_IN_FLIGHT = Gauge("redis_in_flight", "Number of in-flight Redis operations")


def monitored_redis(func):
    """Redis decorator"""

    def wrapper(*args, **kwargs):
        REDIS_IN_FLIGHT.inc()
        start = time.time()
        try:
            result = func(*args, **kwargs)
            # 判斷是 GET 還是 SET
            if func.__name__.startswith("get"):
                REDIS_GET_COUNT.inc()
            else:
                REDIS_SET_COUNT.inc()
            return result
        except Exception as e:
            REDIS_ERROR.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            REDIS_LATENCY.observe(time.time() - start)
            REDIS_IN_FLIGHT.dec()

    return wrapper
