import pytest
import asyncio
from unittest.mock import MagicMock
from app.planner.planner import Planner

@pytest.fixture
def mock_ollama_client():
    client = MagicMock()
    # Mock return values as needed
    return client

@pytest.fixture
def planner(mock_ollama_client):
    p = Planner()
    p.client = mock_ollama_client
    return p
