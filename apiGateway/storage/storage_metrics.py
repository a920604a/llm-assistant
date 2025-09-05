import time

from prometheus_client import Counter, Histogram

# DB metrics
DB_QUERY_COUNT = Counter("db_query_total", "Total number of DB queries")
DB_QUERY_LATENCY = Histogram("db_query_latency_seconds", "DB query latency")
DB_QUERY_ERROR = Counter("db_query_error_total", "Total DB query errors")


def monitored_db(func):
    """DB query decorator"""

    def wrapper(*args, **kwargs):
        DB_QUERY_COUNT.inc()
        start = time.time()
        try:
            return func(*args, **kwargs)
        except Exception:
            DB_QUERY_ERROR.inc()
            raise
        finally:
            DB_QUERY_LATENCY.observe(time.time() - start)

    return wrapper
