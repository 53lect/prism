"""
Capa 6: Síntesis Claude — analiza TODOS los pares en una sola llamada.
"""

import anthropic
import json
import time
from ..config import ANTHROPIC_API_KEY

# Cache en memoria: {symbol: {result, price, timestamp}}
_cache: dict[str, dict] = {}
CACHE_TTL_SECONDS = 900         # 15 minutos
PRICE_CHANGE_THRESHOLD = 0.005  # 0.5%


def _cache_valid(symbol: str, current_price: float) -> bool:
    if symbol not in _cache:
        return False
    entry = _cache[symbol]
    if time.time() - entry["timestamp"] > CACHE_TTL_SECONDS:
        return False
    price_change = abs(current_price - entry["price"]) / entry["price"]
    return price_change < PRICE_CHANGE_THRESHOLD


def _build_pair_block(symbol: str, market: dict, sentiment: dict, news: dict, macro: dict, risk: dict) -> str:
    headlines = "\n".join(f"    - {h}" for h in news.get("headlines", [])) or "    Sin noticias."
    return f"""
  PAR: {symbol}
    Precio: ${market['price']:,.4f} | Cambio 24h: {market['change_24h']:+.2f}% | RSI: {market['rsi_14']} | Volatilidad: {market['volatility']:.3f}%
    Funding rate: {market['funding_rate']:+.4f}% | Open interest: ${market['open_interest']/1e6:.1f}M | Liquidez: {market['liquidity_score']}/100
    Sentimiento: Fear & Greed {sentiment['fear_greed_index']} ({sentiment['fear_greed_label']})
    Noticias ({news['news_count']}): score {news['sentiment_score']:+.2f}
{headlines}
    BTC Dominance: {macro['btc_dominance']:.1f}% | Mercado 24h: {macro['market_cap_change_24h']:+.2f}% | Tendencia: {macro['market_trend']}
    EV ajustado a fees: {risk['expected_value']:+.4f}% | Break-even: {risk['fee_breakeven_pct']:.3f}% | Risk score: {risk['risk_score']}/100
    Señal matemáticamente válida: {'SI' if risk['valid'] else 'NO'}"""


def _build_batch_prompt(pairs_data: list[dict]) -> str:
    blocks = "\n".join(
        _build_pair_block(p["symbol"], p["market"], p["sentiment"], p["news"], p["macro"], p["risk"])
        for p in pairs_data
    )

    symbols = [p["symbol"] for p in pairs_data]

    return f"""Eres el motor de análisis de Prism, un sistema de trading crypto para short trades de 2-8 horas en futuros perpetuos de Binance.

CONTEXTO:
- Capital ~$500, leverage máximo x3
- Fees round-trip: ~0.24% del movimiento necesario para break-even
- Solo operar si el movimiento esperado supera 2x los fees

DATOS DE MERCADO:
{blocks}

INSTRUCCIONES:
Analiza cada par y genera una señal. Usa lenguaje simple y directo — nada de jerga técnica.
- "el mercado está en pánico" en lugar de "Fear & Greed en Extreme Fear"
- "precio cayó 3% hoy" en lugar de "cambio 24h negativo"
- Si el EV es negativo, igual indica la tendencia dominante
- Siempre incluye una sugerencia de trade aunque no sea aconsejable operar

RESPONDE con un JSON array, un objeto por par, en este orden exacto: {symbols}

[
  {{
    "signal": "SHORT" | "LONG" | "NEUTRAL",
    "confidence": 0-100,
    "stop_loss_pct": número,
    "take_profit_pct": número,
    "reasoning": "2-3 oraciones en lenguaje simple explicando qué está pasando",
    "key_risk": "principal riesgo en 1 oración simple",
    "trade_suggestion": {{
      "direction": "SHORT" | "LONG",
      "entry_note": "nivel o condición de entrada sugerida en 1 oración",
      "advisable": true | false,
      "reason": "por qué sí o no operar ahora en 1 oración"
    }}
  }}
]"""


async def analyze_batch(pairs_data: list[dict]) -> dict[str, dict]:
    """Analiza todos los pares en una sola llamada a Claude. Retorna {symbol: result}."""

    # Separar los que tienen cache válido
    to_analyze = []
    results: dict[str, dict] = {}

    for p in pairs_data:
        symbol = p["symbol"]
        current_price = p["market"].get("price", 0)
        if _cache_valid(symbol, current_price):
            cached = _cache[symbol]["result"].copy()
            cached["from_cache"] = True
            results[symbol] = cached
        else:
            to_analyze.append(p)

    if not to_analyze:
        return results

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_batch_prompt(to_analyze)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = next((b.text for b in message.content if b.type == "text"), "[]")

    try:
        # Remover markdown code block si viene envuelto en ```json ... ```
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("```", 2)[1]
            if clean.startswith("json"):
                clean = clean[4:]
        start = clean.find("[")
        end = clean.rfind("]") + 1
        parsed: list[dict] = json.loads(clean[start:end])
    except Exception:
        parsed = []

    for i, p in enumerate(to_analyze):
        symbol = p["symbol"]
        current_price = p["market"].get("price", 0)
        risk = p["risk"]

        if i < len(parsed):
            result = parsed[i]
        else:
            result = {
                "signal": "NEUTRAL",
                "confidence": 0,
                "stop_loss_pct": risk["stop_loss_pct"],
                "take_profit_pct": risk["take_profit_pct"],
                "reasoning": "Error parseando respuesta de Claude.",
                "key_risk": "N/A",
                "trade_suggestion": {
                    "direction": "NEUTRAL",
                    "entry_note": "N/A",
                    "advisable": False,
                    "reason": "Error en análisis.",
                },
            }

        result["from_cache"] = False
        _cache[symbol] = {"result": result, "price": current_price, "timestamp": time.time()}
        results[symbol] = result

    return results


# Compatibilidad con analyze_pair individual (para el endpoint POST /analyze/{pair})
async def analyze(symbol: str, market: dict, sentiment: dict, news: dict, macro: dict, risk: dict) -> dict:
    pair_data = {"symbol": symbol, "market": market, "sentiment": sentiment, "news": news, "macro": macro, "risk": risk}
    results = await analyze_batch([pair_data])
    return results[symbol]
