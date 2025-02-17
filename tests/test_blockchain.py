import pytest
from unittest.mock import Mock, patch
from solders.pubkey import Pubkey
from src.blockchain.solana_client import SolanaClient
from src.blockchain.token_manager import TokenManager


@pytest.fixture
async def mock_solana_client():
    client = SolanaClient("https://api.mainnet-beta.solana.com", "mainnet-beta")
    client.client = Mock()
    return client


@pytest.fixture
async def mock_token_manager(mock_solana_client):
    token_mint = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    return TokenManager(mock_solana_client.client, token_mint)


@pytest.mark.asyncio
async def test_solana_client_initialization(mock_solana_client):
    mock_solana_client.client.get_version.return_value = {"result": "1.0.0"}

    await mock_solana_client.initialize()
    assert mock_solana_client._initialized == True
    mock_solana_client.client.get_version.assert_called_once()


@pytest.mark.asyncio
async def test_token_supply_fetch(mock_solana_client):
    mock_solana_client.client.get_token_supply.return_value = {
        "result": {"value": {"amount": "1000000"}}
    }

    token_mint = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    supply = await mock_solana_client.get_token_supply(token_mint)

    assert supply == "1000000"
    mock_solana_client.client.get_token_supply.assert_called_once_with(token_mint)


@pytest.mark.asyncio
async def test_token_account_creation(mock_token_manager):
    owner = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    mock_token_manager.client.get_account_info.return_value = {"result": {"value": None}}

    await mock_token_manager.create_token_account(owner)

    mock_token_manager.client.send_transaction.assert_called_once()


@pytest.mark.asyncio
async def test_knowledge_transaction_submission(mock_solana_client):
    mock_solana_client._initialized = True
    mock_solana_client.client.send_transaction.return_value = {
        "result": "transaction_signature"
    }

    knowledge_data = {
        "content": "test content",
        "signature": b"test_signature"
    }

    result = await mock_solana_client.submit_knowledge_transaction(
        knowledge_data,
        b"test_signature"
    )

    assert result == "transaction_signature"
    mock_solana_client.client.send_transaction.assert_called_once()


@pytest.mark.asyncio
async def test_transaction_verification(mock_solana_client):
    mock_solana_client.client.confirm_transaction.return_value = {
        "result": {"value": True}
    }

    result = await mock_solana_client.verify_transaction("test_signature")

    assert result == True
    mock_solana_client.client.confirm_transaction.assert_called_once_with("test_signature")


@pytest.mark.asyncio
async def test_token_balance_fetch(mock_token_manager):
    token_account = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    mock_token_manager.client.get_token_account_balance.return_value = {
        "result": {"value": {"amount": "500"}}
    }

    balance = await mock_token_manager.get_token_balance(token_account)

    assert balance == "500"
    mock_token_manager.client.get_token_account_balance.assert_called_once_with(token_account)