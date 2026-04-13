"""
Binance market data fetcher + technical indicators.
Usa la API pública de Binance (no requiere autenticación).
"""

import httpx
import statistics
from dataclasses import dataclass


BINANCE_SPOT = "https://api.binance.com"
BINANCE_FUTURES = "https://fapi.binance.com"


@dataclass
class MarketData:
    symbol: str
    price: float
    change_24h: float        # % cambio 24h
    volume_24h: float        # volumen en USDT
    high_24h: float
    low_24h: float
    funding_rate: float      # tasa de financiamiento actual (futuros)
    open_interest: float     # interés abierto en USDT
    rsi_14: float            # RSI 14 períodos (velas 1h)
    volatility: float        # desviación estándar de retornos (24h)
    liquidity_score: float   # score 0-100 basado en volumen + spread


def _compute_rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0  # neutral si no hay suficientes datos

    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = statistics.mean(gains[-period:])
    avg_loss = statistics.mean(losses[-period:])

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _compute_volatility(closes: list[float]) -> float:
    if len(closes) < 2:
        return 0.0
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
    return statistics.stdev(returns) * 100  # como porcentaje


def _liquidity_score(volume_24h: float, spread_pct: float) -> float:
    # Score simple: volumen alto + spread bajo = mejor liquidez
    vol_score = min(volume_24h / 1_000_000_000, 1.0) * 70  # max 70 pts por volumen >= 1B USDT
    spread_score = max(0, 30 - spread_pct * 1000)           # max 30 pts por spread bajo
    return round(vol_score + spread_score, 1)


async def fetch_market_data(symbol: str) -> MarketData:
    """Obtiene datos de mercado completos para un par (ej: 'DOGEUSDT')."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Stats 24h (spot)
        ticker = (await client.get(f"{BINANCE_SPOT}/api/v3/ticker/24hr", params={"symbol": symbol})).json()

        # 2. Funding rate (futuros perpetuos)
        try:
            funding = (await client.get(f"{BINANCE_FUTURES}/fapi/v1/premiumIndex", params={"symbol": symbol})).json()
            funding_rate = float(funding.get("lastFundingRate", 0)) * 100  # como %
        except Exception:
            funding_rate = 0.0

        # 3. Open interest (futuros)
        try:
            oi = (await client.get(f"{BINANCE_FUTURES}/fapi/v1/openInterest", params={"symbol": symbol})).json()
            open_interest = float(oi.get("openInterest", 0)) * float(ticker["lastPrice"])
        except Exception:
            open_interest = 0.0

        # 4. Velas 1h (últimas 48 para RSI 14 + volatilidad)
        klines = (await client.get(
            f"{BINANCE_SPOT}/api/v3/klines",
            params={"symbol": symbol, "interval": "1h", "limit": 48}
        )).json()
        closes = [float(k[4]) for k in klines]

    price = float(ticker["lastPrice"])
    high = float(ticker["highPrice"])
    low = float(ticker["lowPrice"])
    spread_pct = (high - low) / price if price > 0 else 0
    volume_usdt = float(ticker["quoteVolume"])

    return MarketData(
        symbol=symbol,
        price=price,
        change_24h=float(ticker["priceChangePercent"]),
        volume_24h=volume_usdt,
        high_24h=high,
        low_24h=low,
        funding_rate=funding_rate,
        open_interest=open_interest,
        rsi_14=round(_compute_rsi(closes), 1),
        volatility=round(_compute_volatility(closes), 3),
        liquidity_score=_liquidity_score(volume_usdt, spread_pct),
    )


async def fetch_multiple(symbols: list[str]) -> list[MarketData]:
    """Obtiene datos para múltiples pares en paralelo."""
    import asyncio
    tasks = [fetch_market_data(s) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid = []
    for symbol, result in zip(symbols, results):
        if isinstance(result, Exception):
            print(f"  [WARN] Error fetching {symbol}: {result}")
        else:
            valid.append(result)
    return valid
