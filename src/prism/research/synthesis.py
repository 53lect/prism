"""
Síntesis via Claude: combina datos de mercado + noticias por par
y genera un reporte + ranking de pares volátiles.
"""

import anthropic
from .market import MarketData
from .news import NewsSummary


def _format_market(m: MarketData) -> str:
    return f"""
  Precio: ${m.price:,.4f}
  Cambio 24h: {m.change_24h:+.2f}%
  Volumen 24h: ${m.volume_24h:,.0f}
  High/Low 24h: ${m.high_24h:,.4f} / ${m.low_24h:,.4f}
  Funding rate: {m.funding_rate:+.4f}%
  Open interest: ${m.open_interest:,.0f}
  RSI (14h): {m.rsi_14}
  Volatilidad (std dev retornos 1h): {m.volatility:.3f}%
  Liquidez score: {m.liquidity_score}/100"""


def _format_news(n: NewsSummary) -> str:
    if not n.items:
        return "  Sin noticias disponibles."
    lines = [f"  Sentimiento: {n.bullish_count} bullish / {n.bearish_count} bearish / {n.neutral_count} neutral (score: {n.sentiment_score:+.2f})"]
    for item in n.items[:5]:
        lines.append(f"  - [{item.sentiment.upper()}] {item.title} ({item.source})")
    return "\n".join(lines)


def _build_prompt(market_list: list[MarketData], news_list: list[NewsSummary]) -> str:
    news_by_symbol = {n.symbol: n for n in news_list}

    sections = []
    for m in market_list:
        currency = m.symbol.replace("USDT", "")
        news = news_by_symbol.get(currency)
        section = f"""
=== {m.symbol} ===
DATOS DE MERCADO:{_format_market(m)}

NOTICIAS RECIENTES:
{_format_news(news) if news else "  Sin datos de noticias."}"""
        sections.append(section)

    return f"""Eres un analista de trading crypto especializado en short trades con capital pequeño.

Analiza los siguientes pares candidatos para seleccionar los 3 MEJORES para operar en futuros perpetuos de Binance con short trades de corta duración (2-8 horas).

CRITERIOS DE SELECCIÓN (en orden de importancia):
1. Volatilidad real medida (std dev retornos) — mayor = más oportunidades de ganancia
2. Volumen / liquidez — necesitamos entrar y salir sin mover el precio
3. Comportamiento diferenciado de BTC — correlación alta = sin valor analítico extra
4. Funding rate — si es muy negativo, ir short tiene costo extra
5. Sentimiento de noticias — debe tener confluencia o ser neutral (no contra la señal)

PARES CANDIDATOS:
{"".join(sections)}

RESPONDE EN ESTE FORMATO EXACTO:

ANÁLISIS POR PAR:
[Para cada par: fortalezas, debilidades, veredicto]

TOP 3 SELECCIONADOS:
1. [SÍMBOLO] — [razón principal en 1 línea]
2. [SÍMBOLO] — [razón principal en 1 línea]
3. [SÍMBOLO] — [razón principal en 1 línea]

DESCARTADOS:
[Los que no entraron y por qué en 1 línea cada uno]

ADVERTENCIAS:
[Cualquier riesgo específico a tener en cuenta]"""


async def synthesize(market_list: list[MarketData], news_list: list[NewsSummary], api_key: str) -> str:
    """Llama a Claude Opus para generar el reporte de selección de pares."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(market_list, news_list)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extraer solo el texto (no el bloque de thinking)
    for block in message.content:
        if block.type == "text":
            return block.text

    return "Sin respuesta generada."
