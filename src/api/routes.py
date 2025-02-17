from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from src.blockchain.solana_client import SolanaClient
from src.ai.knowledge_exchange import KnowledgeExchange
from datetime import datetime

router = APIRouter()


class KnowledgeSubmission(BaseModel):
    content: dict
    domain: str
    contributor: str
    metadata: dict
    dependencies: List[dict] = []
    version: str
    timestamp: Optional[str] = None


class QueryParams(BaseModel):
    domain: str
    filters: dict = {}
    limit: int = 10


@router.post("/knowledge/submit")
async def submit_knowledge(
        submission: KnowledgeSubmission,
        exchange: KnowledgeExchange = Depends(lambda: router.knowledge_exchange)
):
    try:
        if not submission.timestamp:
            submission.timestamp = datetime.now().isoformat()

        knowledge_data = submission.dict()
        transaction_id = await exchange.submit_knowledge(knowledge_data)

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": "Knowledge submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/query")
async def query_knowledge(
        query: QueryParams,
        exchange: KnowledgeExchange = Depends(lambda: router.knowledge_exchange)
):
    try:
        results = await exchange.query_knowledge(
            query.domain,
            query.filters
        )

        return {
            "status": "success",
            "results": results[:query.limit],
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{domain}")
async def get_domain_stats(
        domain: str,
        exchange: KnowledgeExchange = Depends(lambda: router.knowledge_exchange)
):
    try:
        pathway = exchange.learning_pathways.get(domain)
        if not pathway:
            raise HTTPException(status_code=404, detail="Domain not found")

        contributors = await pathway.get_top_contributors()

        return {
            "status": "success",
            "total_knowledge": len(pathway.knowledge_graph),
            "top_contributors": contributors,
            "performance_metrics": pathway.performance_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def initialize_router(knowledge_exchange: KnowledgeExchange):
    router.knowledge_exchange = knowledge_exchange
    return router