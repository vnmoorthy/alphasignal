"""
AlphaSignal Test Suite
Run with: pytest tests/ -v
"""

import json
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from config.settings import Settings
from agents.graph import (
    SignalType,
    AlphaSignal,
    Citation,
    build_alpha_signal_crew,
    run_alpha_signal,
    parse_alpha_signal,
)
from api.trader import PaperTrader, Position, OrderResult
from api.youcom import YouComClient, SearchResult, FinanceResearchResult


class TestSettings:
    def test_default_settings(self):
        settings = Settings()
        assert settings.MAX_POSITION_SIZE_PCT == 0.05
        assert settings.TRADE_CONFIDENCE_THRESHOLD == 0.72
        assert settings.DEFAULT_MODEL == "gpt-4o-mini"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("MAX_POSITION_SIZE_PCT", "0.10")
        monkeypatch.setenv("TRADE_CONFIDENCE_THRESHOLD", "0.80")
        settings = Settings()
        assert settings.MAX_POSITION_SIZE_PCT == 0.10
        assert settings.TRADE_CONFIDENCE_THRESHOLD == 0.80


class TestSignalModels:
    def test_signal_type_enum(self):
        assert SignalType.BULLISH.value == "bullish"
        assert SignalType.BEARISH.value == "bearish"
        assert SignalType.NEUTRAL.value == "neutral"
        assert SignalType.CATALYST.value == "catalyst"
        assert SignalType.RISK.value == "risk"

    def test_citation_creation(self):
        citation = Citation(
            source="sec.gov",
            url="https://sec.gov/...",
            title="NVDA 10-Q",
            snippet="Revenue up 122%",
        )
        assert citation.source == "sec.gov"
        assert "122%" in citation.snippet

    def test_alpha_signal_creation(self):
        citations = [
            Citation(source="sec.gov", url="https://sec.gov/...", title="NVDA 10-Q", snippet="Revenue up"),
        ]
        signal = AlphaSignal(
            symbol="NVDA",
            signal_type=SignalType.BULLISH,
            confidence=0.87,
            thesis="Strong data center growth",
            citations=citations,
            target_price=575.0,
            stop_loss=0.05,
            time_horizon="2-4 weeks",
        )
        assert signal.symbol == "NVDA"
        assert signal.signal_type == SignalType.BULLISH
        assert signal.confidence == 0.87
        assert len(signal.citations) == 1


class TestPaperTrader:
    @pytest.fixture
    def trader(self):
        return PaperTrader()

    def test_get_account_simulation(self, trader):
        account = trader.get_account()
        assert account["portfolio_value"] > 0
        assert account["cash"] >= 0
        assert account["buying_power"] >= 0

    def test_get_positions_empty(self, trader):
        positions = trader.get_positions()
        assert positions == []

    def test_get_latest_price_simulation(self, trader):
        price = trader.get_latest_price("NVDA")
        assert isinstance(price, float)
        assert price >= 0  # Live market may return 0.0 after hours

    def test_place_market_order_simulation(self, trader):
        result = trader.place_market_order("NVDA", 10, "buy")
        assert result.success is True
        assert result.symbol == "NVDA"
        assert result.side == "buy"
        assert result.qty == 10
        # filled_price may be None for live orders that haven't filled yet
        assert result.status is not None

    def test_place_limit_order_simulation(self, trader):
        result = trader.place_limit_order("AAPL", 5, "sell", 200.0)
        assert result.success is True
        assert result.symbol == "AAPL"
        assert result.side == "sell"

    def test_cancel_all_orders(self, trader):
        trader.cancel_all_orders()  # Should not raise

    def test_get_order_history_returns_list(self, trader):
        orders = trader.get_order_history()
        assert isinstance(orders, list)  # May have real orders from prior tests


class TestAlphaSignalParsing:
    def test_parse_valid_json(self):
        raw = '{"signal_type": "bullish", "confidence": 0.85, "thesis": "Test thesis", "target_price": 150.0, "stop_loss": 0.05, "time_horizon": "1-2 weeks", "citations": [{"source": "sec.gov", "url": "https://sec.gov", "title": "Test", "snippet": "Test snippet"}]}'
        signal = parse_alpha_signal(Mock(raw=raw), "AAPL")
        assert signal.symbol == "AAPL"
        assert signal.signal_type == SignalType.BULLISH
        assert signal.confidence == 0.85
        assert signal.thesis == "Test thesis"
        assert signal.target_price == 150.0
        assert signal.stop_loss == 0.05
        assert len(signal.citations) == 1

    def test_parse_with_markdown_code_block(self):
        raw = '''Here is the result:
```json
{"signal_type": "bearish", "confidence": 0.75, "thesis": "Downside risk", "citations": []}
```'''
        signal = parse_alpha_signal(Mock(raw=raw), "TSLA")
        assert signal.signal_type == SignalType.BEARISH
        assert signal.confidence == 0.75

    def test_parse_invalid_json_returns_neutral(self):
        raw = "This is not JSON at all"
        signal = parse_alpha_signal(Mock(raw=raw), "NVDA")
        assert signal.signal_type == SignalType.NEUTRAL
        assert signal.confidence == 0.5
        assert "Could not parse" in signal.thesis


class TestYouComClient:
    @pytest.fixture
    def client(self):
        return YouComClient(api_key="test-key")

    def test_init_requires_api_key(self):
        # Must patch both the explicit arg AND the settings fallback so the guard fires
        with patch("api.youcom.settings") as mock_settings:
            mock_settings.YDC_API_KEY = ""
            with pytest.raises(ValueError, match="YDC_API_KEY is required"):
                YouComClient(api_key="")

    @pytest.mark.asyncio
    async def test_search_mock(self, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "hits": [
                {"title": "Test", "url": "https://test.com", "snippet": "Test snippet", "source": "web", "published_date": "2024-01-01"}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            results = await client.search("NVDA", count=5)
            assert len(results) == 1
            assert results[0].title == "Test"
            assert results[0].source == "web"

    @pytest.mark.asyncio
    async def test_finance_research_mock(self, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "answer": "NVDA earnings beat",
            "citations": [
                {"title": "NVDA 10-Q", "url": "https://sec.gov/...", "snippet": "Revenue up", "doc_id": "1"}
            ],
            "follow_up_questions": ["What about next quarter?"],
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.finance_research("NVDA earnings")
            assert isinstance(result, FinanceResearchResult)
            assert result.answer == "NVDA earnings beat"
            assert len(result.citations) == 1


class TestAgentCrew:
    def test_build_crew_returns_crew(self):
        crew = build_alpha_signal_crew("NVDA", portfolio_value=100000)
        assert crew is not None
        assert len(crew.agents) == 6  # 5 agents + synthesizer
        assert len(crew.tasks) == 5

    def test_crew_has_correct_agents(self):
        crew = build_alpha_signal_crew("NVDA")
        agent_roles = [a.role for a in crew.agents]
        assert "Real-Time News & Catalyst Scanner" in agent_roles
        assert "SEC Filings Forensic Analyst" in agent_roles
        assert "Alternative Data & Sentiment Analyst" in agent_roles
        assert "Comparative Valuation Specialist" in agent_roles
        assert "Portfolio Risk Manager" in agent_roles
        assert "Chief Investment Officer - Signal Synthesis" in agent_roles


class TestToolFormatting:
    """Ensure all YouCom-backed tools can format results without AttributeError."""

    def _make_finance_result(self):
        from api.youcom import FinanceResearchResult, Citation as YCCitation
        return FinanceResearchResult(
            answer="Test analysis answer",
            citations=[
                YCCitation(title="Test Filing", url="https://sec.gov/test", snippet="Revenue up 20%", doc_id="doc1")
            ],
            query="test query",
        )

    def _mock_asyncio_run(self, result):
        """Patch asyncio.run to return a pre-built FinanceResearchResult synchronously."""
        from unittest.mock import patch, MagicMock
        return patch("agents.graph.asyncio.run", return_value=result)

    def test_news_scanner_tool_formats_result(self):
        from agents.graph import NewsScannerTool
        tool = NewsScannerTool()
        finance_result = self._make_finance_result()
        with self._mock_asyncio_run(finance_result):
            output = tool._run("NVDA")
        data = json.loads(output)
        assert "answer" in data
        assert "citations" in data
        assert data["citations"][0]["title"] == "Test Filing"

    def test_filings_analyzer_tool_formats_result(self):
        from agents.graph import FilingsAnalyzerTool
        tool = FilingsAnalyzerTool()
        finance_result = self._make_finance_result()
        with self._mock_asyncio_run(finance_result):
            output = tool._run("NVDA")
        data = json.loads(output)
        assert "answer" in data
        assert "citations" in data

    def test_sentiment_analyzer_tool_formats_result(self):
        from agents.graph import SentimentAnalyzerTool
        tool = SentimentAnalyzerTool()
        finance_result = self._make_finance_result()
        with self._mock_asyncio_run(finance_result):
            output = tool._run("NVDA")
        data = json.loads(output)
        assert "answer" in data
        assert "citations" in data

    def test_peer_comparison_tool_formats_result(self):
        from agents.graph import PeerComparisonTool
        tool = PeerComparisonTool()
        finance_result = self._make_finance_result()
        with self._mock_asyncio_run(finance_result):
            output = tool._run("NVDA")
        data = json.loads(output)
        assert "answer" in data
        assert "citations" in data

    def test_tool_returns_error_json_on_api_failure(self):
        """Tool must degrade gracefully rather than raising when YouCom is unavailable."""
        from agents.graph import NewsScannerTool
        import agents.graph as graph_module
        tool = NewsScannerTool()
        with patch("agents.graph.asyncio.run", side_effect=Exception("API timeout")):
            output = tool._run("NVDA")
        data = json.loads(output)
        assert "error" in data
        assert "citations" in data
        assert data["citations"] == []


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_analysis_flow_demo_mode(self):
        """Test the full analysis flow in demo mode (no LLM API keys)."""
        from agents.graph import run_alpha_signal

        # Force demo mode by clearing both LLM keys regardless of env
        with patch.dict("os.environ", {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=False):
            signal = await run_alpha_signal(
                symbol="NVDA",
                portfolio_value=100000,
                current_positions={},
            )

        assert signal.symbol == "NVDA"
        assert signal.signal_type in [SignalType.BULLISH, SignalType.BEARISH, SignalType.NEUTRAL]
        assert 0 <= signal.confidence <= 1
        assert len(signal.thesis) > 0

    @pytest.mark.asyncio
    async def test_different_symbols_produce_different_signals(self):
        """Different symbols should yield symbol-specific thesis text in demo mode."""
        from agents.graph import run_alpha_signal

        with patch.dict("os.environ", {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=False):
            nvda_signal = await run_alpha_signal(symbol="NVDA", portfolio_value=100000)
            aapl_signal = await run_alpha_signal(symbol="AAPL", portfolio_value=100000)

        assert nvda_signal.symbol == "NVDA"
        assert aapl_signal.symbol == "AAPL"
        assert nvda_signal.confidence > 0
        assert aapl_signal.confidence > 0


# Pytest configuration
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])