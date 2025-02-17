import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture(autouse=True)
async def setup_teardown():
    # Setup
    yield
    # Teardown