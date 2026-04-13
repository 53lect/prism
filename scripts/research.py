"""
Research Agent — CLI para selección de pares volátiles.

Uso:
    uv run python scripts/research.py --pairs DOGE PEPE AVAX LINK ARB WIF
"""

import asyncio
import sys
import os

# Forzar UTF-8 en la terminal de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
load_dotenv()

import typer
from prism.research.market import fetch_multiple
from prism.research.news import fetch_news_multiple
from prism.research.synthesis import synthesize

app = typer.Typer()

DEFAULT_CANDIDATES = ["DOGEUSDT", "PEPEUSDT", "AVAXUSDT", "LINKUSDT", "ARBUSDT", "WIFUSDT"]


@app.command()
def main(
    pairs: str = typer.Option("", "--pairs", "-p", help="Pares separados por coma (ej: DOGE,PEPE,AVAX)"),
    no_news: bool = typer.Option(False, "--no-news", help="Saltar fetch de noticias"),
):
    """Analiza pares crypto candidatos y recomienda los 3 mejores para short trading."""
    symbols = [p.strip() for p in pairs.split(",")] if pairs else DEFAULT_CANDIDATES
    # Normalizar: agregar USDT si no tiene
    symbols = [s.upper() if s.upper().endswith("USDT") else s.upper() + "USDT" for s in symbols]
    currencies = [s.replace("USDT", "") for s in symbols]

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY", "")

    typer.echo(f"\nAnalizando {len(symbols)} pares: {', '.join(symbols)}")
    typer.echo("=" * 60)

    async def run():
        # Paso 1: Market data
        typer.echo("\n[1/3] Obteniendo datos de mercado...")
        market_data = await fetch_multiple(symbols)
        typer.echo(f"  OK {len(market_data)} pares obtenidos")
        for m in market_data:
            typer.echo(f"  {m.symbol}: ${m.price:.4f} | {m.change_24h:+.2f}% | Vol: ${m.volume_24h/1e6:.0f}M | RSI: {m.rsi_14}")

        # Paso 2: Noticias
        news_data = []
        if not no_news:
            typer.echo("\n[2/3] Obteniendo noticias (CryptoPanic)...")
            news_data = await fetch_news_multiple(currencies, cryptopanic_key)
            for n in news_data:
                typer.echo(f"  {n.symbol}: {len(n.items)} noticias | score: {n.sentiment_score:+.2f}")
        else:
            typer.echo("\n[2/3] Noticias omitidas (--no-news)")

        # Paso 3: Síntesis Claude
        if not anthropic_key:
            typer.echo("\nERROR: ANTHROPIC_API_KEY no configurada en .env", err=True)
            raise typer.Exit(1)
        typer.echo("\n[3/3] Sintetizando con Claude Opus...")
        report = await synthesize(market_data, news_data, anthropic_key)

        typer.echo("\n" + "=" * 60)
        typer.echo("REPORTE DE SELECCIÓN DE PARES")
        typer.echo("=" * 60)
        typer.echo(report)
        typer.echo("=" * 60)

    asyncio.run(run())


if __name__ == "__main__":
    app()
