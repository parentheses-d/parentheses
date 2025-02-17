from fastapi import FastAPI
from src.api.routes import router
from src.api.handlers import setup_handlers
from src.blockchain.solana_client import SolanaClient
from src.ai.knowledge_exchange import KnowledgeExchange
from src.config.settings import settings

app = FastAPI(
    title="Parentheses Protocol",
    description="A protocol for collaborative AI learning on Solana blockchain",
    version="1.0.0"
)

# Initialize Solana client
solana_client = SolanaClient(
    rpc_url=settings.SOLANA_RPC_URL,
    network=settings.SOLANA_NETWORK
)

# Initialize Knowledge Exchange
knowledge_exchange = KnowledgeExchange(
    solana_client=solana_client,
    validation_threshold=settings.VALIDATION_THRESHOLD
)

# Setup handlers
setup_handlers(app)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    await solana_client.initialize()
    await knowledge_exchange.start_exchange_cycle()

@app.on_event("shutdown")
async def shutdown_event():
    await solana_client.cleanup()
    await knowledge_exchange.stop_exchange_cycle()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )