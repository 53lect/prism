"""
Capa 2: Sentimiento — Fear & Greed Index (alternative.me, gratuito sin API key).
"""

import httpx

FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"


async def analyze() -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(FEAR_GREED_URL)
            resp.raise_for_status()
            data = resp.json()["data"][0]
            value = int(data["value"])
            label = data["value_classification"]
        except Exception:
            value, label = 50, "Neutral"

    # Score normalizado: -1.0 (extreme fear) a +1.0 (extreme greed)
    score = (value - 50) / 50

    return {
        "fear_greed_index": value,
        "fear_greed_label": label,
        "sentiment_score": round(score, 2),
        # Mercado en miedo extremo (<25) = potencial rebote (bullish)
        # Mercado en codicia extrema (>75) = potencial corrección (bearish)
        "bias": "bullish" if value < 30 else "bearish" if value > 70 else "neutral",
    }
