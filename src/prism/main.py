"""
Pipeline principal de Prism — orquesta las 6 capas de análisis.
"""

import asyncio
from .layers import market_data, sentiment, news, macro, risk, synthesis
from .db.models import init_db, get_session, PairAnalysis
from .config import ANTHROPIC_API_KEY, ALL_PAIRS


async def analyze_pair(symbol: str, capital: float = 500.0, leverage: float = 3.0) -> dict:
    """Corre el pipeline completo de 6 capas para un par. Retorna el análisis completo."""
    currency = symbol.replace("USDT", "")

    # Capas 1-4 en paralelo (no dependen entre sí)
    market_result, sentiment_result, news_result, macro_result = await asyncio.gather(
        market_data.analyze(symbol),
        sentiment.analyze(),
        news.analyze(currency),
        macro.analyze(),
    )

    # Capa 5: Risk (necesita market data)
    risk_result = risk.analyze(market_result, capital=capital, leverage=leverage)

    # Capa 6: Síntesis Claude (una sola llamada, con cache)
    synthesis_result = await synthesis.analyze(
        symbol, market_result, sentiment_result, news_result, macro_result, risk_result
    )

    return {
        "symbol": symbol,
        "market": market_result,
        "sentiment": sentiment_result,
        "news": news_result,
        "macro": macro_result,
        "risk": risk_result,
        "synthesis": synthesis_result,
    }


def save_analysis(result: dict) -> None:
    """Persiste el resultado en SQLite."""
    m = result["market"]
    s = result["sentiment"]
    n = result["news"]
    mac = result["macro"]
    r = result["risk"]
    syn = result["synthesis"]

    record = PairAnalysis(
        symbol=result["symbol"],
        price=m["price"],
        change_24h=m["change_24h"],
        volume_24h=m["volume_24h"],
        rsi_14=m["rsi_14"],
        volatility=m["volatility"],
        funding_rate=m["funding_rate"],
        open_interest=m["open_interest"],
        fear_greed_index=s["fear_greed_index"],
        fear_greed_label=s["fear_greed_label"],
        sentiment_score=s["sentiment_score"],
        news_count=n["news_count"],
        news_sentiment_score=n["sentiment_score"],
        news_summary="; ".join(n.get("headlines", [])[:3]),
        btc_dominance=mac["btc_dominance"],
        market_trend=mac["market_trend"],
        position_size_pct=r["position_size_pct"],
        fee_breakeven_pct=r["fee_breakeven_pct"],
        expected_value=r["expected_value"],
        risk_score=r["risk_score"],
        signal=syn.get("signal", "NEUTRAL"),
        confidence=syn.get("confidence", 0),
        reasoning=syn.get("reasoning", ""),
        stop_loss_pct=syn.get("stop_loss_pct", 0),
        take_profit_pct=syn.get("take_profit_pct", 0),
        valid=r["valid"],
    )

    with get_session() as session:
        session.add(record)
        session.commit()


def format_signal(result: dict) -> str:
    """Formatea el resultado para mostrar en terminal."""
    syn = result["synthesis"]
    r = result["risk"]
    m = result["market"]
    cached = " [CACHE]" if syn.get("from_cache") else ""

    signal = syn.get("signal", "NEUTRAL")
    confidence = syn.get("confidence", 0)
    lines = [
        f"\n{'='*55}",
        f"  {result['symbol']} | {signal} {confidence}%{cached}",
        f"{'='*55}",
        f"  Precio:     ${m['price']:,.4f}  |  RSI: {m['rsi_14']}  |  Vol: ${m['volume_24h']/1e6:.0f}M",
        f"  Position:   {r['position_size_pct']}% capital (${r['position_size_usd']:.0f})",
        f"  Stop-loss:  -{syn.get('stop_loss_pct') or r['stop_loss_pct']:.3f}%",
        f"  Take-profit: +{syn.get('take_profit_pct') or r['take_profit_pct']:.3f}%",
        f"  Break-even: {r['fee_breakeven_pct']:.3f}% (fees)",
        f"  EV:         {r['expected_value']:+.4f}%",
        f"",
        f"  {syn.get('reasoning', '')}",
        f"  RIESGO: {syn.get('key_risk', '')}",
        f"{'='*55}",
    ]
    return "\n".join(lines)


async def run_all(capital: float = 500.0, leverage: float = 3.0) -> list[dict]:
    """Analiza todos los pares configurados."""
    init_db()
    results = []
    for symbol in ALL_PAIRS:
        print(f"  Analizando {symbol}...")
        result = await analyze_pair(symbol, capital, leverage)
        save_analysis(result)
        results.append(result)
    return results
