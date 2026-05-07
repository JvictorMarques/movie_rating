from opentelemetry import metrics

meter = metrics.get_meter(__name__)

http_request = meter.create_counter(
    name='http_request',
    description='Number of HTTP requests',
    unit='1',
)

http_request_duration = meter.create_histogram(
    name='http_request_duration',
    description='Duration of HTTP requests',
    unit='s',
)
