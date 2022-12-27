from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.config import settings


def configure_tracer() -> None:
    """Начальная конфигурация Open Telemetry"""
    resource = Resource(attributes={SERVICE_NAME: "auth-service"})

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger.host,
        agent_port=settings.jaeger.port,
    )

    provider = TracerProvider(resource=resource)
    jaeger_processor = BatchSpanProcessor(jaeger_exporter)

    provider.add_span_processor(jaeger_processor)
    trace.set_tracer_provider(provider)
