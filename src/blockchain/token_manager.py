from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from spl.token.constants import TOKEN_PROGRAM_ID
import asyncio
import logging


class TokenManager:
    def __init__(self, solana_client: AsyncClient, token_mint: Pubkey):
        self.client = solana_client
        self.token_mint = token_mint
        self.logger = logging.getLogger(__name__)

    async def create_token_account(self, owner: Pubkey) -> Pubkey:
        try:
            associated_token_address = get_associated_token_address(
                owner,
                self.token_mint
            )

            if not await self._account_exists(associated_token_address):
                instruction = create_associated_token_account(
                    payer=owner,
                    owner=owner,
                    mint=self.token_mint
                )
                await self.client.send_transaction(instruction)

            return associated_token_address
        except Exception as e:
            self.logger.error(f"Failed to create token account: {str(e)}")
            raise

    async def get_token_balance(self, token_account: Pubkey) -> int:
        try:
            balance = await self.client.get_token_account_balance(token_account)
            return balance['result']['value']['amount']
        except Exception as e:
            self.logger.error(f"Failed to get token balance: {str(e)}")
            raise

    async def distribute_rewards(self, recipient: Pubkey, amount: int) -> str:
        try:
            token_account = await self.create_token_account(recipient)

            transfer_instruction = self._create_transfer_instruction(
                token_account,
                amount
            )

            result = await self.client.send_transaction(transfer_instruction)
            return result['result']
        except Exception as e:
            self.logger.error(f"Failed to distribute rewards: {str(e)}")
            raise

    async def _account_exists(self, address: Pubkey) -> bool:
        try:
            account_info = await self.client.get_account_info(address)
            return account_info['result']['value'] is not None
        except Exception:
            return False

    def _create_transfer_instruction(self, recipient: Pubkey, amount: int):
        return {
            'programId': TOKEN_PROGRAM_ID,
            'keys': [
                {'pubkey': self.token_mint, 'isSigner': True, 'isWritable': True},
                {'pubkey': recipient, 'isSigner': False, 'isWritable': True}
            ],
            'data': bytes([2, *amount.to_bytes(8, 'little')])
        }