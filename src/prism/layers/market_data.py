"""Capa 1: Market data — reutiliza research/market.py con output estructurado."""

from ..research.market import fetch_market_data, MarketData


async def analyze(symbol: str) -> dict:
    m: MarketData = await fetch_market_data(symbol)
    return {
        "price": m.price,
        "change_24h": m.change_24h,
        "volume_24h": m.volume_24h,
        "high_24h": m.high_24h,
        "low_24h": m.low_24h,
        "funding_rate": m.funding_rate,
        "open_interest": m.open_interest,
        "rsi_14": m.rsi_14,
        "volatility": m.volatility,
        "liquidity_score": m.liquidity_score,
        "bias": "bearish" if m.rsi_14 > 65 else "bullish" if m.rsi_14 < 35 else "neutral",
    }
