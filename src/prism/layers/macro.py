"""
Capa 4: Macro — BTC dominance y tendencia general del mercado crypto.
Usa CoinGecko global endpoint (gratuito).
"""

import httpx

COINGECKO_GLOBAL = "https://api.coingecko.com/api/v3/global"


async def analyze() -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(COINGECKO_GLOBAL)
            resp.raise_for_status()
            data = resp.json()["data"]
            btc_dominance = data["market_cap_percentage"].get("btc", 0)
            total_market_cap_change = data.get("market_cap_change_percentage_24h_usd", 0)
        except Exception:
            btc_dominance = 50.0
            total_market_cap_change = 0.0

    # BTC dominance alta (>55%) = mercado risk-off, altcoins bajo presión
    # BTC dominance baja (<45%) = altseason, mayor apetito de riesgo
    if btc_dominance > 55:
        market_trend = "btc_dominance"   # altcoins bajo presión
        bias = "bearish"
    elif btc_dominance < 45:
        market_trend = "altseason"
        bias = "neutral"
    else:
        market_trend = "balanced"
        bias = "neutral"

    return {
        "btc_dominance": round(btc_dominance, 2),
        "market_cap_change_24h": round(total_market_cap_change, 2),
        "market_trend": market_trend,
        "bias": bias,
    }
