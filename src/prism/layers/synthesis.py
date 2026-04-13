"""
Capa 6: Síntesis Claude Opus — combina las 5 capas y genera señal direccional.
"""

import anthropic
import time
from ..config import ANTHROPIC_API_KEY

# Cache en memoria: {symbol: {result, price, timestamp}}
_cache: dict[str, dict] = {}
CACHE_TTL_SECONDS = 900        # 15 minutos
PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% — si el precio no cambió más de esto, reutiliza


def _cache_valid(symbol: str, current_price: float) -> bool:
    if symbol not in _cache:
        return False
    entry = _cache[symbol]
    age = time.time() - entry["timestamp"]
    if age > CACHE_TTL_SECONDS:
        return False
    price_change = abs(current_price - entry["price"]) / entry["price"]
    return price_change < PRICE_CHANGE_THRESHOLD


def _build_prompt(symbol: str, market: dict, sentiment: dict, news: dict, macro: dict, risk: dict) -> str:
    headlines = "\n".join(f"  - {h}" for h in news.get("headlines", [])) or "  Sin noticias disponibles."

    return f"""Eres el motor de síntesis de Prism, un sistema de análisis de trading crypto para short trades de 2-8 horas en futuros perpetuos de Binance.

CONTEXTO CRÍTICO:
- Capital pequeño (~$500), leverage máximo x{risk['leverage']}
- Fee round-trip: {risk['fee_breakeven_pct']:.3f}% del movimiento necesario para break-even
- Señal SOLO válida si el profit esperado supera {risk['fee_breakeven_pct'] * 2:.3f}% (2x fees)

PAR: {symbol}

CAPA 1 - MARKET DATA:
  Precio: ${market['price']:,.4f}
  Cambio 24h: {market['change_24h']:+.2f}%
  Volumen 24h: ${market['volume_24h']/1e6:.1f}M USDT
  RSI (14h): {market['rsi_14']} → bias: {market['bias']}
  Volatilidad (std dev 1h): {market['volatility']:.3f}%
  Funding rate: {market['funding_rate']:+.4f}%
  Open interest: ${market['open_interest']/1e6:.1f}M USDT
  Liquidez score: {market['liquidity_score']}/100

CAPA 2 - SENTIMIENTO:
  Fear & Greed Index: {sentiment['fear_greed_index']} ({sentiment['fear_greed_label']}) → bias: {sentiment['bias']}

CAPA 3 - NOTICIAS ({news['news_count']} encontradas):
  Score sentimiento: {news['sentiment_score']:+.2f} → bias: {news['bias']}
{headlines}

CAPA 4 - MACRO:
  BTC Dominance: {macro['btc_dominance']:.1f}%
  Mercado 24h: {macro['market_cap_change_24h']:+.2f}%
  Tendencia: {macro['market_trend']} → bias: {macro['bias']}

CAPA 5 - RISK:
  Position size sugerido: {risk['position_size_pct']}% del capital (${risk['position_size_usd']:.0f} en posición)
  Break-even mínimo: {risk['fee_breakeven_pct']:.3f}%
  Movimiento esperado 4h: {risk['expected_move_pct']:.3f}%
  Expected Value: {risk['expected_value']:+.4f}%
  VaR 95%: {risk['var_95_pct']:.3f}%
  Risk score: {risk['risk_score']}/100
  Señal matemáticamente válida: {'SI' if risk['valid'] else 'NO - EV insuficiente'}

INSTRUCCIONES:
Analiza la confluencia de las 5 capas y genera una señal de trading. Si la mayoría de los bias son contradictorios o el EV es insuficiente, emite NEUTRAL.

RESPONDE EXACTAMENTE en este formato JSON:
{{
  "signal": "SHORT" | "LONG" | "NEUTRAL",
  "confidence": 0-100,
  "stop_loss_pct": número,
  "take_profit_pct": número,
  "reasoning": "2-3 oraciones explicando la confluencia de señales",
  "key_risk": "principal riesgo de esta operación en 1 oración"
}}"""


async def analyze(symbol: str, market: dict, sentiment: dict, news: dict, macro: dict, risk: dict) -> dict:
    import json
    current_price = market.get("price", 0)

    # Verificar cache antes de llamar a Claude
    if _cache_valid(symbol, current_price):
        cached = _cache[symbol]["result"].copy()
        cached["from_cache"] = True
        return cached

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_prompt(symbol, market, sentiment, news, macro, risk)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = next((b.text for b in message.content if b.type == "text"), "{}")

    # Extraer JSON de la respuesta
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        result = json.loads(text[start:end])
    except Exception:
        result = {
            "signal": "NEUTRAL",
            "confidence": 0,
            "stop_loss_pct": risk["stop_loss_pct"],
            "take_profit_pct": risk["take_profit_pct"],
            "reasoning": "Error parseando respuesta de Claude.",
            "key_risk": "N/A",
        }

    result["from_cache"] = False

    # Guardar en cache
    _cache[symbol] = {
        "result": result,
        "price": current_price,
        "timestamp": time.time(),
    }

    return result
