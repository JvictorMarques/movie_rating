import logging
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider  # noqa: PLC2701
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (  # noqa: PLC2701
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import (  # noqa: PLC2701
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import (  # noqa: PLC2701
    BatchLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import (  # noqa: PLC2701
    ExplicitBucketHistogramAggregation,
)
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.attributes.service_attributes import (
    SERVICE_NAME,
    SERVICE_VERSION,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.settings import Settings

settings = Settings()


def _get_version() -> str:
    try:
        return version('movie-rating')
    except PackageNotFoundError:
        return 'unknown'


def setup_telemetry(app: FastAPI, engine: AsyncEngine) -> None:
    resource = Resource({
        SERVICE_NAME: 'movie-rating',
        SERVICE_VERSION: _get_version(),
        'deployment.environment': settings.ENVIRONMENT,
    })

    metric_exporter = OTLPMetricExporter(
        endpoint=settings.OTLP_ENDPOINT, insecure=True
    )
    metric_reader = PeriodicExportingMetricReader(metric_exporter)

    _http_boundaries = [
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ]
    http_duration_view = View(
        instrument_name='http_request_duration',
        aggregation=ExplicitBucketHistogramAggregation(_http_boundaries),
    )

    metrics.set_meter_provider(
        MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
            views=[http_duration_view],
        )
    )

    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
        )
    )
    trace.set_tracer_provider(trace_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
        )
    )
    set_logger_provider(logger_provider)

    otel_handler = LoggingHandler(
        level=logging.INFO, logger_provider=logger_provider
    )
    logging.basicConfig(
        level=logging.INFO,
        format=''
        '%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s',
        handlers=[otel_handler],
    )

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
