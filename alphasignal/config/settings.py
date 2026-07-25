import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # You.com APIs
    YDC_API_KEY: str = os.getenv("YDC_API_KEY", "")
    YDC_SEARCH_ENDPOINT: str = "https://api.you.com/search"
    YDC_RESEARCH_ENDPOINT: str = "https://api.you.com/research"
    YDC_FINANCE_ENDPOINT: str = "https://api.you.com/finance"

    # Parasail
    PARASAIL_API_KEY: str = os.getenv("PARASAIL", os.getenv("PARASAIL_API_KEY", ""))
    PARASAIL_BASE_URL: str = "https://api.parasail.ai/v1"

    # CrewAI / LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEFAULT_MODEL: str = "gpt-4o-mini"

    # Paper Trading (Alpaca)
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"

    # Opsera
    OPSERA_TOKEN: str = os.getenv("OPSERA_TOKEN", "")
    OPSERA_ORG: str = os.getenv("OPSERA_ORG", "")

    # Render
    RENDER_API_KEY: str = os.getenv("RENDER_API_KEY", "")

    # App
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENT_AGENTS: int = 5
    TRADE_CONFIDENCE_THRESHOLD: float = 0.72
    MAX_POSITION_SIZE_PCT: float = 0.05

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()