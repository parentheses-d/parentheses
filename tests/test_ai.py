import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.ai.knowledge_exchange import KnowledgeExchange
from src.ai.validation import KnowledgeValidator
from src.ai.learning_pathway import LearningPathway


@pytest.fixture
def mock_solana_client():
    return Mock()


@pytest.fixture
def knowledge_validator():
    return KnowledgeValidator(threshold=0.85)


@pytest.fixture
def learning_pathway():
    return LearningPathway(domain="test_domain")


@pytest.fixture
async def knowledge_exchange(mock_solana_client):
    exchange = KnowledgeExchange(
        solana_client=mock_solana_client,
        validation_threshold=0.85
    )
    return exchange


@pytest.mark.asyncio
async def test_knowledge_submission(knowledge_exchange):
    knowledge_data = {
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
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

    knowledge_exchange.solana_client.submit_knowledge_transaction.return_value = "tx_id"

    result = await knowledge_exchange.submit_knowledge(knowledge_data)
    assert result == "tx_id"


def test_knowledge_validation(knowledge_validator):
    valid_knowledge = {
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
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

    assert knowledge_validator._validate_structure(valid_knowledge) == True


@pytest.mark.asyncio
async def test_learning_pathway_knowledge_addition(learning_pathway):
    knowledge_data = {
        "id": "test_id",
        "content": "test_content",
        "contributor": "test_user"
    }

    await learning_pathway.add_knowledge("test_id", knowledge_data)
    assert "test_id" in learning_pathway.knowledge_graph
    assert learning_pathway.contributor_scores["test_user"] == 1


@pytest.mark.asyncio
async def test_knowledge_query(learning_pathway):
    knowledge_data = {
        "id": "test_id",
        "content": "test_content",
        "domain": "test_domain",
        "contributor": "test_user"
    }

    await learning_pathway.add_knowledge("test_id", knowledge_data)

    query_params = {"domain": "test_domain"}
    results = await learning_pathway.query_knowledge(query_params)

    assert len(results) == 1
    assert results[0]["content"] == "test_content"


@pytest.mark.asyncio
async def test_performance_metrics_calculation(learning_pathway):
    knowledge_data = {
        "id": "test_id",
        "content": "test_content",
        "timestamp": datetime.now().isoformat(),
        "usage_count": 10
    }

    await learning_pathway._calculate_performance_metrics("test_id")
    assert "test_id" in learning_pathway.performance_metrics


@pytest.mark.asyncio
async def test_pathway_optimization(learning_pathway):
    knowledge_data1 = {
        "id": "test_id1",
        "content": "test_content1",
        "contributor": "test_user"
    }
    knowledge_data2 = {
        "id": "test_id2",
        "content": "test_content2",
        "contributor": "test_user"
    }

    await learning_pathway.add_knowledge("test_id1", knowledge_data1)
    await learning_pathway.add_knowledge("test_id2", knowledge_data2)

    await learning_pathway.optimize_pathways()

    assert len(learning_pathway.performance_metrics) == 2


@pytest.mark.asyncio
async def test_top_contributors(learning_pathway):
    knowledge_data1 = {
        "id": "test_id1",
        "content": "test_content1",
        "contributor": "user1"
    }
    knowledge_data2 = {
        "id": "test_id2",
        "content": "test_content2",
        "contributor": "user2"
    }

    await learning_pathway.add_knowledge("test_id1", knowledge_data1)
    await learning_pathway.add_knowledge("test_id2", knowledge_data2)

    contributors = await learning_pathway.get_top_contributors()
    assert len(contributors) == 2