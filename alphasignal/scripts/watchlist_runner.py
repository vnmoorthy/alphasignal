#!/usr/bin/env python3
"""
Watchlist runner - continuously monitors symbols and generates signals
Run this as a background worker for continuous alpha generation
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import List, Dict, Set

from config.settings import settings
from agents.graph import run_alpha_signal, AlphaSignal, SignalType
from api import paper_trader, YouComClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("watchlist")


class WatchlistRunner:
    def __init__(
        self,
        symbols: List[str],
        interval: int = 300,
        portfolio_value: float = 100000,
        auto_trade: bool = False,
        min_confidence: float = 0.72,
    ):
        self.symbols = [s.upper() for s in symbols]
        self.interval = interval
        self.portfolio_value = portfolio_value
        self.auto_trade = auto_trade
        self.min_confidence = min_confidence
        self.running = False
        self.signals_generated = 0
        self.trades_executed = 0
        self.errors = 0
        self.last_signals: Dict[str, AlphaSignal] = {}

    async def run_scan(self, symbol: str) -> AlphaSignal:
        """Run agent swarm on a single symbol"""
        logger.info(f"Scanning {symbol}...")
        try:
            positions = {p.symbol: p.market_value for p in paper_trader.get_positions()}
            signal = await run_alpha_signal(
                symbol=symbol,
                portfolio_value=self.portfolio_value,
                current_positions=positions,
            )
            return signal
        except Exception as e:
            logger.error(f"Scan failed for {symbol}: {e}")
            raise

    async def evaluate_and_trade(self, signal: AlphaSignal):
        """Evaluate signal and execute trade if criteria met"""
        logger.info(
            f"Signal: {signal.symbol} | {signal.signal_type.value.upper()} | "
            f"Confidence: {signal.confidence:.1%} | Citations: {len(signal.citations)}"
        )

        if signal.confidence < self.min_confidence:
            logger.info(f"  -> Below confidence threshold ({self.min_confidence:.0%})")
            return

        if signal.signal_type == SignalType.NEUTRAL:
            logger.info("  -> Neutral signal, no action")
            return

        self.signals_generated += 1
        self.last_signals[signal.symbol] = signal

        if self.auto_trade:
            await self.execute_trade(signal)

    async def execute_trade(self, signal: AlphaSignal):
        """Execute paper trade based on signal"""
        try:
            account = paper_trader.get_account()
            portfolio_value = account["portfolio_value"]
            position_size = portfolio_value * settings.MAX_POSITION_SIZE_PCT * signal.confidence
            price = paper_trader.get_latest_price(signal.symbol)
            qty = int(position_size / price)

            if qty <= 0:
                logger.warning(f"  -> Position size too small for {signal.symbol}")
                return

            side = "buy" if signal.signal_type == SignalType.BULLISH else "sell"
            logger.info(f"  -> Executing {side.upper()} {qty} {signal.symbol} @ ~${price:.2f}")

            result = paper_trader.place_market_order(signal.symbol, qty, side)

            if result.success:
                logger.info(f"  -> FILLED: {result.order_id} @ ${result.filled_price:.2f}")
                self.trades_executed += 1
            else:
                logger.error(f"  -> REJECTED: {result.error}")

        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            self.errors += 1

    async def run_cycle(self):
        """Single scan cycle across all symbols"""
        logger.info(f"{'='*60}")
        logger.info(f"Watchlist cycle started | {len(self.symbols)} symbols | {datetime.utcnow().isoformat()}Z")

        for symbol in self.symbols:
            try:
                signal = await self.run_scan(symbol)
                await self.evaluate_and_trade(signal)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                self.errors += 1

        logger.info(f"Cycle complete | Signals: {self.signals_generated} | Trades: {self.trades_executed} | Errors: {self.errors}")
        logger.info(f"{'='*60}\n")

    async def run(self):
        """Main run loop"""
        self.running = True
        logger.info(f"Starting watchlist runner: {self.symbols} | Interval: {self.interval}s | Auto-trade: {self.auto_trade}")

        # Initial scan
        await self.run_cycle()

        while self.running:
            try:
                await asyncio.sleep(self.interval)
                if self.running:
                    await self.run_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                self.errors += 1
                await asyncio.sleep(60)  # Back off on error

    def stop(self):
        self.running = False


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="AlphaSignal Watchlist Runner")
    parser.add_argument("symbols", nargs="+", help="Symbols to watch (e.g., NVDA MSFT AAPL)")
    parser.add_argument("--interval", type=int, default=300, help="Scan interval in seconds")
    parser.add_argument("--portfolio", type=float, default=100000, help="Portfolio value")
    parser.add_argument("--auto-trade", action="store_true", help="Execute paper trades automatically")
    parser.add_argument("--min-confidence", type=float, default=0.72, help="Minimum confidence threshold")
    args = parser.parse_args()

    runner = WatchlistRunner(
        symbols=args.symbols,
        interval=args.interval,
        portfolio_value=args.portfolio,
        auto_trade=args.auto_trade,
        min_confidence=args.min_confidence,
    )

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, runner.stop)

    try:
        await runner.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        logger.info(
            f"Final stats | Cycles: {runner.signals_generated} | "
            f"Trades: {runner.trades_executed} | Errors: {runner.errors}"
        )


if __name__ == "__main__":
    asyncio.run(main())