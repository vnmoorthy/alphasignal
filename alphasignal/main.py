#!/usr/bin/env python3
"""
AlphaSignal - Real-Time Alpha Hunter
Main orchestration script for the You.com hackathon.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

from config.settings import settings
from agents import build_alpha_signal_crew, run_alpha_signal, AlphaSignal, SignalType
from api import paper_trader, YouComClient

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger(__name__)

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]AlphaSignal[/bold cyan] - Real-Time Alpha Hunter\n"
        "[dim]You.com Hackathon | Track 1: Real-Time Intelligence[/dim]",
        border_style="cyan",
    ))


def print_signal(signal: AlphaSignal):
    color_map = {
        SignalType.BULLISH: "green",
        SignalType.BEARISH: "red",
        SignalType.NEUTRAL: "yellow",
        SignalType.CATALYST: "cyan",
        SignalType.RISK: "red",
    }
    color = color_map.get(signal.signal_type, "white")

    table = Table(title=f"AlphaSignal: {signal.symbol}", border_style=color)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Signal", f"[{color}]{signal.signal_type.value.upper()}[/{color}]")
    table.add_row("Confidence", f"{signal.confidence:.1%}")
    table.add_row("Thesis", signal.thesis)
    if signal.target_price:
        table.add_row("Target Price", f"${signal.target_price:.2f}")
    if signal.stop_loss:
        table.add_row("Stop Loss", f"{signal.stop_loss:.1%}")
    table.add_row("Time Horizon", signal.time_horizon)
    table.add_row("Citations", str(len(signal.citations)))

    console.print(table)

    if signal.citations:
        console.print("\n[bold]Citation Trail:[/bold]")
        for i, c in enumerate(signal.citations, 1):
            console.print(f"  [{i}] {c.title} ({c.source})")
            console.print(f"      [link={c.url}]{c.url}[/link]")


async def run_analysis(symbol: str, portfolio_value: float = 100000):
    print_banner()
    console.print(f"\n[bold]Analyzing {symbol.upper()}...[/bold]\n")

    positions = {p.symbol: p.market_value for p in paper_trader.get_positions()}
    account = paper_trader.get_account()

    console.print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
    console.print(f"Cash: ${account['cash']:,.2f}")
    console.print(f"Current Positions: {positions or 'None'}\n")

    # Use Rich Progress for beautiful agent tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running agent swarm...", total=6)
        
        # Run the signal generation
        signal = await run_alpha_signal(
            symbol=symbol.upper(),
            portfolio_value=portfolio_value,
            current_positions=positions,
        )
        
        progress.update(task, advance=6, description="[green]Analysis complete!")

    print_signal(signal)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"signal_{signal.symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "symbol": signal.symbol,
            "signal_type": signal.signal_type.value,
            "confidence": signal.confidence,
            "thesis": signal.thesis,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "time_horizon": signal.time_horizon,
            "citations": [
                {
                    "source": c.source,
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                }
                for c in signal.citations
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }, f, indent=2)

    console.print(f"\n[green]Signal saved to {output_file}[/green]")

    if signal.confidence >= settings.TRADE_CONFIDENCE_THRESHOLD and signal.signal_type in (SignalType.BULLISH, SignalType.BEARISH):
        console.print("\n[bold yellow]Confidence exceeds threshold. Execute trade?[/bold yellow]")
        if click.confirm("Place paper trade?"):
            await execute_trade(signal)

    return signal


async def execute_trade(signal: AlphaSignal):
    account = paper_trader.get_account()
    portfolio_value = account["portfolio_value"]
    position_size = portfolio_value * settings.MAX_POSITION_SIZE_PCT * signal.confidence
    price = paper_trader.get_latest_price(signal.symbol)
    qty = int(position_size / price)

    if qty == 0:
        console.print("[red]Position size too small[/red]")
        return

    side = "buy" if signal.signal_type == SignalType.BULLISH else "sell"
    console.print(f"\nPlacing {side.upper()} order: {qty} shares of {signal.symbol} @ ~${price:.2f}")

    result = paper_trader.place_market_order(signal.symbol, qty, side)

    if result.success:
        console.print(f"[green]Order filled: {result.order_id} @ ${result.filled_price:.2f}[/green]")
    else:
        console.print(f"[red]Order failed: {result.error}[/red]")


async def run_watchlist(symbols: List[str], interval: int = 300):
    """Run continuous monitoring on a watchlist"""
    print_banner()
    console.print(f"\n[bold]Monitoring watchlist: {', '.join(s.upper() for s in symbols)}[/bold]")
    console.print(f"Interval: {interval}s | Press Ctrl+C to stop\n")

    try:
        while True:
            for symbol in symbols:
                console.print(f"\n{'='*60}")
                await run_analysis(symbol)
            console.print(f"\n[dim]Sleeping {interval}s...[/dim]")
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Watchlist stopped[/yellow]")


@click.group()
def cli():
    """AlphaSignal - Real-Time Alpha Hunter for You.com Hackathon"""
    pass


@cli.command()
@click.argument("symbol")
@click.option("--portfolio", default=100000, help="Portfolio value for position sizing")
def analyze(symbol: str, portfolio: float):
    """Run full agent swarm analysis on a symbol"""
    asyncio.run(run_analysis(symbol, portfolio))


@cli.command()
@click.argument("symbols", nargs=-1)
@click.option("--interval", default=300, help="Seconds between scans")
def watch(symbols: tuple, interval: int):
    """Continuous monitoring of watchlist"""
    if not symbols:
        console.print("[red]Provide at least one symbol[/red]")
        return
    asyncio.run(run_watchlist(list(symbols), interval))


@cli.command()
def account():
    """Show paper trading account status"""
    print_banner()
    account = paper_trader.get_account()
    positions = paper_trader.get_positions()

    console.print(Panel(f"""
[bold]Portfolio Value:[/bold] ${account['portfolio_value']:,.2f}
[bold]Cash:[/bold] ${account['cash']:,.2f}
[bold]Buying Power:[/bold] ${account['buying_power']:,.2f}
    """, title="Account", border_style="blue"))

    if positions:
        table = Table(title="Positions")
        table.add_column("Symbol")
        table.add_column("Qty", justify="right")
        table.add_column("Entry", justify="right")
        table.add_column("Current", justify="right")
        table.add_column("P&L", justify="right")
        table.add_column("P&L %", justify="right")

        for p in positions:
            color = "green" if p.unrealized_pl >= 0 else "red"
            table.add_row(
                p.symbol,
                f"{p.qty:.0f}",
                f"${p.avg_entry_price:.2f}",
                f"${p.market_value/p.qty:.2f}" if p.qty else "N/A",
                f"[{color}]${p.unrealized_pl:.2f}[/{color}]",
                f"[{color}]{p.unrealized_plpc:.2%}[/{color}]",
            )
        console.print(table)
    else:
        console.print("[dim]No open positions[/dim]")


@cli.command()
@click.argument("symbol")
@click.argument("qty", type=int)
@click.argument("side", type=click.Choice(["buy", "sell"]))
def trade(symbol: str, qty: int, side: str):
    """Manual paper trade"""
    result = paper_trader.place_market_order(symbol.upper(), qty, side)
    if result.success:
        console.print(f"[green]Order filled: {result.order_id} @ ${result.filled_price:.2f}[/green]")
    else:
        console.print(f"[red]Order failed: {result.error}[/red]")


@cli.command()
def test_api():
    """Test You.com API connectivity"""
    print_banner()
    console.print("\n[bold]Testing You.com APIs...[/bold]\n")

    client = YouComClient()

    async def test():
        try:
            console.print("Testing Search API...")
            results = await client.search("NVDA earnings", count=3)
            console.print(f"[green]✓ Search: {len(results)} results[/green]")

            console.print("Testing Finance Research API...")
            finance = await client.finance_research("NVDA upcoming earnings date and consensus")
            console.print(f"[green]✓ Finance Research: {len(finance.citations)} citations[/green]")

            console.print("Testing Deep Research API...")
            research = await client.deep_research("NVDA competitive position vs AMD in AI chips")
            console.print(f"[green]✓ Deep Research: {len(research.citations)} citations[/green]")

            console.print("\n[bold green]All APIs working![/bold green]")
        except Exception as e:
            console.print(f"[red]API test failed: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(test())


@cli.command()
def demo():
    """Run the hackathon demo presentation"""
    from scripts.demo import main as demo_main
    asyncio.run(demo_main())


if __name__ == "__main__":
    cli()