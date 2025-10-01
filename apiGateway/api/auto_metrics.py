import asyncio
import time
from functools import wraps

from prometheus_client import Counter, Gauge, Histogram

# 紀錄各個 endpoint 的 metrics
_METRICS_REGISTRY = {}


def observe_api(func):
    """
    FastAPI API 監控，涵蓋四個黃金訊號：
    - Latency: Histogram
    - Traffic: Counter
    - Errors: Counter
    - Saturation: Gauge (併發中請求數)
    """

    service_name = "api-gateway"
    endpoint_name = func.__name__

    # 如果還沒創建，就創建
    if endpoint_name not in _METRICS_REGISTRY:
        counter = Counter(
            f"{endpoint_name}_total",
            f"Total requests to {endpoint_name}",
            ["endpoint", "app_service"],
        )
        error_counter = Counter(
            f"{endpoint_name}_error_total",
            f"Error requests to {endpoint_name}",
            ["endpoint", "app_service", "error_type"],
        )
        histogram = Histogram(
            f"{endpoint_name}_latency_seconds",
            f"Latency for {endpoint_name}",
            ["endpoint", "app_service"],
            buckets=[0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5],
        )
        in_flight = Gauge(
            f"{endpoint_name}_in_flight",
            f"In-flight requests for {endpoint_name}",
            ["endpoint", "app_service"],
        )

        _METRICS_REGISTRY[endpoint_name] = {
            "counter": counter.labels(endpoint=endpoint_name, app_service=service_name),
            "error_counter": error_counter.labels(
                endpoint=endpoint_name, app_service=service_name, error_type="unknown"
            ),
            "histogram": histogram.labels(
                endpoint=endpoint_name, app_service=service_name
            ),
            "in_flight": in_flight.labels(
                endpoint=endpoint_name, app_service=service_name
            ),
        }

    metrics = _METRICS_REGISTRY[endpoint_name]

    def record_metrics(e=None):
        if e is not None:
            metrics["error_counter"].labels(
                endpoint=endpoint_name,
                app_service=service_name,
                error_type=type(e).__name__,
            ).inc()

    async def async_wrapper(*args, **kwargs):
        metrics["counter"].inc()
        metrics["in_flight"].inc()
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            record_metrics(e)
            raise
        finally:
            metrics["histogram"].observe(time.time() - start)
            metrics["in_flight"].dec()

    def sync_wrapper(*args, **kwargs):
        metrics["counter"].inc()
        metrics["in_flight"].inc()
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            record_metrics(e)
            raise
        finally:
            metrics["histogram"].observe(time.time() - start)
            metrics["in_flight"].dec()

    if asyncio.iscoroutinefunction(func):
        return wraps(func)(async_wrapper)
    return wraps(func)(sync_wrapper)
