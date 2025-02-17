from src.blockchain.solana_client import SolanaClient
from src.ai.validation import KnowledgeValidator
from src.ai.learning_pathway import LearningPathway
import asyncio
import json
import hashlib
import logging
from typing import Dict, List


class KnowledgeExchange:
    def __init__(self, solana_client: SolanaClient, validation_threshold: float):
        self.solana_client = solana_client
        self.validator = KnowledgeValidator(threshold=validation_threshold)
        self.learning_pathways: Dict[str, LearningPathway] = {}
        self.logger = logging.getLogger(__name__)
        self._exchange_task = None

    async def start_exchange_cycle(self):
        self._exchange_task = asyncio.create_task(self._run_exchange_cycle())
        self.logger.info("Knowledge exchange cycle started")

    async def stop_exchange_cycle(self):
        if self._exchange_task:
            self._exchange_task.cancel()
            await asyncio.gather(self._exchange_task, return_exceptions=True)
            self.logger.info("Knowledge exchange cycle stopped")

    async def submit_knowledge(self, knowledge_data: dict) -> str:
        try:
            # Validate knowledge structure and content
            if not await self.validator.validate_knowledge(knowledge_data):
                raise ValueError("Knowledge validation failed")

            # Generate unique identifier for knowledge
            knowledge_id = self._generate_knowledge_id(knowledge_data)

            # Create signature for blockchain transaction
            signature = self._create_signature(knowledge_data)

            # Submit to blockchain
            transaction_id = await self.solana_client.submit_knowledge_transaction(
                knowledge_data,
                signature
            )

            # Create learning pathway if new domain
            domain = knowledge_data.get('domain')
            if domain not in self.learning_pathways:
                self.learning_pathways[domain] = LearningPathway(domain)

            # Add knowledge to pathway
            await self.learning_pathways[domain].add_knowledge(
                knowledge_id,
                knowledge_data
            )

            return transaction_id
        except Exception as e:
            self.logger.error(f"Failed to submit knowledge: {str(e)}")
            raise

    async def query_knowledge(self, domain: str, query_params: dict) -> List[dict]:
        try:
            if domain not in self.learning_pathways:
                return []

            pathway = self.learning_pathways[domain]
            results = await pathway.query_knowledge(query_params)

            # Verify results on blockchain
            verified_results = []
            for result in results:
                if await self._verify_knowledge(result):
                    verified_results.append(result)

            return verified_results
        except Exception as e:
            self.logger.error(f"Failed to query knowledge: {str(e)}")
            raise

    async def _run_exchange_cycle(self):
        while True:
            try:
                for pathway in self.learning_pathways.values():
                    await pathway.optimize_pathways()
                    await self._distribute_rewards(pathway)

                await asyncio.sleep(300)  # 5 minutes interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in exchange cycle: {str(e)}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def _verify_knowledge(self, knowledge_data: dict) -> bool:
        try:
            signature = knowledge_data.get('signature')
            if not signature:
                return False

            return await self.solana_client.verify_transaction(signature)
        except Exception:
            return False

    def _generate_knowledge_id(self, knowledge_data: dict) -> str:
        content = json.dumps(knowledge_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _create_signature(self, knowledge_data: dict) -> bytes:
        content = json.dumps(knowledge_data, sort_keys=True)
        return hashlib.sha256(content.encode()).digest()

    async def _distribute_rewards(self, pathway: LearningPathway):
        contributors = await pathway.get_top_contributors()
        for contributor, score in contributors:
            try:
                reward_amount = int(score * 1e9)  # Convert to lamports
                await self.solana_client.token_manager.distribute_rewards(
                    contributor,
                    reward_amount
                )
            except Exception as e:
                self.logger.error(f"Failed to distribute rewards: {str(e)}")