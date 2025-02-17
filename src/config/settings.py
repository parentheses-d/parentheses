import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Network Configuration
    SOLANA_NETWORK = os.getenv("SOLANA_NETWORK", "mainnet-beta")
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

    # Token Configuration
    TOKEN_MINT_ADDRESS = os.getenv("TOKEN_MINT_ADDRESS")
    TOKEN_DECIMALS = 9

    # AI Configuration
    KNOWLEDGE_EXCHANGE_INTERVAL = 300  # seconds
    VALIDATION_THRESHOLD = 0.85
    MAX_LEARNING_PATHWAYS = 100

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///parentheses.db")


settings = Settings()