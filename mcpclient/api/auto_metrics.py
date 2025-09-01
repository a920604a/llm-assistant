import asyncio
import time
from functools import wraps

from prometheus_client import Counter, Histogram

# 紀錄各個 endpoint 的 metrics
_METRICS_REGISTRY = {}


def observe_api(func):
    """
    自動包裝 FastAPI 路由：
    - Counter: 呼叫次數
    - Histogram: 延遲時間
    """
    endpoint_name = func.__name__

    # 如果還沒創建，就創建
    if endpoint_name not in _METRICS_REGISTRY:
        _METRICS_REGISTRY[endpoint_name] = {
            "counter": Counter(
                f"{endpoint_name}_total", f"Total requests to {endpoint_name}"
            ),
            "histogram": Histogram(
                f"{endpoint_name}_latency_seconds", f"Latency for {endpoint_name}"
            ),
        }

    counter = _METRICS_REGISTRY[endpoint_name]["counter"]
    histogram = _METRICS_REGISTRY[endpoint_name]["histogram"]

    if asyncio.iscoroutinefunction(func):
        # async function
        @wraps(func)
        async def wrapper(*args, **kwargs):
            counter.inc()
            start = time.time()
            try:
                result = await func(*args, **kwargs)
            finally:
                histogram.observe(time.time() - start)
            return result

    else:
        # sync function
        @wraps(func)
        def wrapper(*args, **kwargs):
            counter.inc()
            start = time.time()
            try:
                result = func(*args, **kwargs)
            finally:
                histogram.observe(time.time() - start)
            return result

    return wrapper
