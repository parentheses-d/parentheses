from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from src.config.settings import settings
import asyncio
import logging


class SolanaClient:
    def __init__(self, rpc_url: str, network: str):
        self.client = AsyncClient(rpc_url)
        self.network = network
        self.logger = logging.getLogger(__name__)
        self._keypair = None
        self._initialized = False

    async def initialize(self):
        try:
            version = await self.client.get_version()
            self.logger.info(f"Connected to Solana {self.network}, version: {version['result']}")
            self._initialized = True
            await self._initialize_protocol_account()
        except Exception as e:
            self.logger.error(f"Failed to initialize Solana client: {str(e)}")
            raise

    async def _initialize_protocol_account(self):
        if not self._keypair:
            self._keypair = Keypair()

        try:
            balance = await self.client.get_balance(self._keypair.public_key)
            self.logger.info(f"Protocol account balance: {balance['result']['value']} lamports")
        except Exception as e:
            self.logger.error(f"Failed to initialize protocol account: {str(e)}")
            raise

    async def get_token_supply(self, token_mint: Pubkey) -> int:
        try:
            supply = await self.client.get_token_supply(token_mint)
            return supply['result']['value']['amount']
        except Exception as e:
            self.logger.error(f"Failed to get token supply: {str(e)}")
            raise

    async def get_token_holders(self, token_mint: Pubkey) -> list:
        try:
            accounts = await self.client.get_token_accounts_by_owner(
                token_mint,
                {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'}
            )
            return accounts['result']['value']
        except Exception as e:
            self.logger.error(f"Failed to get token holders: {str(e)}")
            raise

    async def submit_knowledge_transaction(self, knowledge_data: dict, signature: bytes) -> str:
        if not self._initialized:
            raise RuntimeError("Solana client not initialized")

        try:
            instruction = self._create_knowledge_instruction(knowledge_data, signature)
            transaction = Transaction().add(instruction)

            signed_tx = self.client.sign_transaction(transaction, self._keypair)
            result = await self.client.send_transaction(signed_tx)

            return result['result']
        except Exception as e:
            self.logger.error(f"Failed to submit knowledge transaction: {str(e)}")
            raise

    async def verify_transaction(self, signature: str) -> bool:
        try:
            result = await self.client.confirm_transaction(signature)
            return result['result']['value']
        except Exception as e:
            self.logger.error(f"Failed to verify transaction: {str(e)}")
            return False

    async def cleanup(self):
        if self._initialized:
            await self.client.close()