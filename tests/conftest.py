import sys
from unittest.mock import MagicMock

for mod in [
    "mlflow",
    "pythonjsonlogger",
    "opentelemetry.exporter.otlp.proto.grpc",
    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
    "opentelemetry.instrumentation.fastapi",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import pytest
import asyncio
from app.planner.planner import Planner


@pytest.fixture
def mock_ollama_client():
    client = MagicMock()
    return client


@pytest.fixture
def planner(mock_ollama_client):
    p = Planner()
    p.client = mock_ollama_client
    return p
