import time

from prometheus_client import Counter, Gauge, Histogram

# DB metrics
DB_QUERY_COUNT = Counter("db_query_total", "Total number of DB queries")
DB_QUERY_LATENCY = Histogram("db_query_latency_seconds", "DB query latency")
DB_QUERY_ERROR = Counter(
    "db_query_error_total", "Total DB query errors", ["error_type"]
)
DB_IN_FLIGHT = Gauge("db_in_flight", "Number of in-flight DB queries")


def monitored_db(func):
    """DB query decorator"""

    def wrapper(*args, **kwargs):
        DB_IN_FLIGHT.inc()
        DB_QUERY_COUNT.inc()
        start = time.time()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            DB_QUERY_ERROR.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            DB_QUERY_LATENCY.observe(time.time() - start)
            DB_IN_FLIGHT.dec()

    return wrapper
