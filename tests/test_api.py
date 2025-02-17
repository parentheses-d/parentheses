import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch
from src.main import app
from src.api.routes import router, KnowledgeSubmission, QueryParams


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_knowledge_exchange():
    return Mock()


def test_knowledge_submission(test_client, mock_knowledge_exchange):
    router.knowledge_exchange = mock_knowledge_exchange
    mock_knowledge_exchange.submit_knowledge.return_value = "tx_id"

    submission_data = {
        "content": {
            "type": "algorithm",
            "algorithm": {
                "name": "test_algo",
                "parameters": {"param1": 1},
                "complexity": "O(n)"
            }
        },
        "domain": "test_domain",
        "contributor": "test_user",
        "metadata": {},
        "dependencies": [],
        "version": "1.0.0"
    }

    response = test_client.post("/api/v1/knowledge/submit", json=submission_data)

    assert response.status_code == 200
    assert response.json()["transaction_id"] == "tx_id"
    mock_knowledge_exchange.submit_knowledge.assert_called_once()


def test_knowledge_query(test_client, mock_knowledge_exchange):
    router.knowledge_exchange = mock_knowledge_exchange
    mock_knowledge_exchange.query_knowledge.return_value = [
        {
            "content": "test_content",
            "domain": "test_domain"
        }
    ]

    query_data = {
        "domain": "test_domain",
        "filters": {},
        "limit": 10
    }

    response = test_client.post("/api/v1/knowledge/query", json=query_data)

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    mock_knowledge_exchange.query_knowledge.assert_called_once()


def test_domain_stats(test_client, mock_knowledge_exchange):
    router.knowledge_exchange = mock_knowledge_exchange

    mock_pathway = Mock()
    mock_pathway.knowledge_graph = {"id1": {}, "id2": {}}
    mock_pathway.get_top_contributors.return_value = [
        ("user1", 10),
        ("user2", 5)
    ]
    mock_pathway.performance_metrics = {
        "id1": 0.8,
        "id2": 0.6
    }

    mock_knowledge_exchange.learning_pathways = {
        "test_domain": mock_pathway
    }

    response = test_client.get("/api/v1/stats/test_domain")

    assert response.status_code == 200
    assert response.json()["total_knowledge"] == 2
    assert len(response.json()["top_contributors"]) == 2


def test_invalid_knowledge_submission(test_client, mock_knowledge_exchange):
    router.knowledge_exchange = mock_knowledge_exchange
    mock_knowledge_exchange.submit_knowledge.side_effect = ValueError("Invalid knowledge")

    submission_data = {
        "content": {},  # Invalid content
        "domain": "test_domain",
        "contributor": "test_user",
        "metadata": {},
        "dependencies": [],
        "version": "1.0.0"
    }

    response = test_client.post("/api/v1/knowledge/submit", json=submission_data)

    assert response.status_code == 400
    assert "Invalid knowledge" in response.json()["detail"]


def test_domain_not_found(test_client, mock_knowledge_exchange):
    router.knowledge_exchange = mock_knowledge_exchange
    mock_knowledge_exchange.learning_pathways = {}

    response = test_client.get("/api/v1/stats/nonexistent_domain")

    assert response.status_code == 404
    assert "Domain not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limiting(test_client):
    for _ in range(101):  # Exceed rate limit (100 requests per minute)
        response = test_client.get("/api/v1/stats/test_domain")

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]


def test_authentication(test_client):
    response = test_client.post(
        "/api/v1/knowledge/submit",
        json={},
        headers={"Authorization": "Invalid"}
    )

    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["error"]