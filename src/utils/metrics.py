from prometheus_client import Counter, Histogram, start_http_server
import time
import os

# Start Prometheus HTTP server
def start_metrics_server(port=8000):
    start_http_server(port)
    print(f"Metrics server started on port {port}")

# Metrics definitions
EMBEDDING_GENERATION_TIME = Histogram(
    'embedding_generation_seconds',
    'Time spent generating embeddings'
)

QUERY_PROCESSING_TIME = Histogram(
    'query_processing_seconds',
    'Time spent processing queries'
)

DB_OPERATION_TIME = Histogram(
    'db_operation_seconds',
    'Time spent on database operations'
)

EMBEDDING_COUNT = Counter(
    'embeddings_generated_total',
    'Total number of embeddings generated'
)

QUERY_COUNT = Counter(
    'queries_processed_total',
    'Total number of queries processed'
)

PII_PROCESSING_TIME = Histogram(
    'pii_processing_seconds',
    'Time spent on PII detection and masking'
)

PII_ENTITIES_DETECTED = Counter(
    'pii_entities_detected_total',
    'Total number of PII entities detected'
)

class MetricsMiddleware:
    @staticmethod
    def track_time(metric):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metric.observe(duration)
                return result
            return wrapper
        return decorator 