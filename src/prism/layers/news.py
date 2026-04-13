"""Capa 3: Noticias — reutiliza research/news.py."""

from ..research.news import fetch_news, NewsSummary


async def analyze(currency: str) -> dict:
    n: NewsSummary = await fetch_news(currency)
    top_headlines = [f"[{i.sentiment.upper()}] {i.title}" for i in n.items[:5]]

    return {
        "news_count": len(n.items),
        "bullish_count": n.bullish_count,
        "bearish_count": n.bearish_count,
        "sentiment_score": n.sentiment_score,
        "headlines": top_headlines,
        "bias": "bullish" if n.sentiment_score > 0.2 else "bearish" if n.sentiment_score < -0.2 else "neutral",
    }
