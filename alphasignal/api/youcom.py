import httpx
import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None


class Citation(BaseModel):
    title: str
    url: str
    snippet: str
    doc_id: str


class FinanceResearchResult(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    query: str
    follow_up_questions: List[str] = Field(default_factory=list)


class ResearchResult(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    query: str
    follow_up_questions: List[str] = Field(default_factory=list)


class YouComClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 60.0):
        self.api_key = api_key or settings.YDC_API_KEY
        if not self.api_key:
            raise ValueError("YDC_API_KEY is required")
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"X-API-Key": self.api_key},
        )

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self.client.post(endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def search(
        self,
        query: str,
        count: int = 10,
        recency_days: int = 7,
        safe_search: str = "moderate",
    ) -> List[SearchResult]:
        """You.com Web Search API - real-time web results with citations"""
        payload = {
            "query": query,
            "count": count,
            "recency_days": recency_days,
            "safe_search": safe_search,
        }
        data = await self._post(settings.YDC_SEARCH_ENDPOINT, payload)
        results = []
        for hit in data.get("hits", []):
            results.append(
                SearchResult(
                    title=hit.get("title", ""),
                    url=hit.get("url", ""),
                    snippet=hit.get("snippet", ""),
                    source=hit.get("source", "web"),
                    published_date=hit.get("published_date"),
                )
            )
        return results

    async def finance_research(
        self,
        query: str,
        detail_level: str = "comprehensive",
        include_citations: bool = True,
    ) -> FinanceResearchResult:
        """You.com Finance Research API - specialized for financial queries with citations"""
        payload = {
            "query": query,
            "detail_level": detail_level,
            "include_citations": include_citations,
        }
        data = await self._post(settings.YDC_FINANCE_ENDPOINT, payload)
        citations = [
            Citation(
                title=c.get("title", ""),
                url=c.get("url", ""),
                snippet=c.get("snippet", ""),
                doc_id=c.get("doc_id", ""),
            )
            for c in data.get("citations", [])
        ]
        return FinanceResearchResult(
            answer=data.get("answer", ""),
            citations=citations,
            query=query,
            follow_up_questions=data.get("follow_up_questions", []),
        )

    async def deep_research(
        self,
        query: str,
        detail_level: str = "comprehensive",
        include_citations: bool = True,
    ) -> ResearchResult:
        """You.com Deep Research API - multi-step research with citations"""
        payload = {
            "query": query,
            "detail_level": detail_level,
            "include_citations": include_citations,
        }
        data = await self._post(settings.YDC_RESEARCH_ENDPOINT, payload)
        citations = [
            Citation(
                title=c.get("title", ""),
                url=c.get("url", ""),
                snippet=c.get("snippet", ""),
                doc_id=c.get("doc_id", ""),
            )
            for c in data.get("citations", [])
        ]
        return ResearchResult(
            answer=data.get("answer", ""),
            citations=citations,
            query=query,
            follow_up_questions=data.get("follow_up_questions", []),
        )

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


# Convenience functions for common financial queries
async def get_earnings_calendar(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Upcoming earnings date, consensus estimates, and historical surprises for {symbol}"
    )


async def get_sec_filings_analysis(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Latest SEC filings (10-K, 10-Q, 8-K) analysis for {symbol}: key risks, MD&A highlights, material changes"
    )


async def get_options_flow(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Unusual options activity, put/call ratio, gamma exposure, and dealer positioning for {symbol}"
    )


async def get_analyst_updates(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Recent analyst rating changes, price target revisions, and estimate revisions for {symbol}"
    )


async def get_news_sentiment(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Latest news sentiment, catalyst events, and social media buzz for {symbol} over past 7 days"
    )


async def get_peer_comparison(symbol: str, client: YouComClient) -> FinanceResearchResult:
    return await client.finance_research(
        f"Peer comparison for {symbol}: valuation multiples, growth rates, margins, and relative performance vs sector"
    )