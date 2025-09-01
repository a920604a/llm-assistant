import time
from functools import wraps

from api.storage_metrics import (
    REDIS_ERROR,
    REDIS_GET_COUNT,
    REDIS_LATENCY,
    REDIS_SET_COUNT,
)


def monitored_redis(func):
    """Redis operation decorator"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            # 自動判斷 GET / SET
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
