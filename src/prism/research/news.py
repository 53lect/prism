"""
News fetcher usando CoinGecko News API (gratuita, sin registro).
Filtra noticias por moneda buscando el ticker en título y descripción.
"""

import httpx
import xml.etree.ElementTree as ET
from dataclasses import dataclass

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
]

BULLISH_KEYWORDS = {"surge", "rally", "bullish", "breakout", "pump", "gain", "up", "high", "buy", "moon"}
BEARISH_KEYWORDS = {"crash", "dump", "bearish", "drop", "fall", "down", "low", "sell", "fear", "decline"}


@dataclass
class NewsItem:
    title: str
    source: str
    published_at: str
    url: str
    votes_positive: int
    votes_negative: int
    sentiment: str  # "bullish" | "bearish" | "neutral"


@dataclass
class NewsSummary:
    symbol: str
    items: list[NewsItem]
    bullish_count: int
    bearish_count: int
    neutral_count: int
    sentiment_score: float  # -1.0 a +1.0


def _detect_sentiment(text: str) -> str:
    words = set(text.lower().split())
    bullish = len(words & BULLISH_KEYWORDS)
    bearish = len(words & BEARISH_KEYWORDS)
    if bullish > bearish:
        return "bullish"
    elif bearish > bullish:
        return "bearish"
    return "neutral"


def _sentiment_score(bullish: int, bearish: int, neutral: int) -> float:
    total = bullish + bearish + neutral
    if total == 0:
        return 0.0
    return round((bullish - bearish) / total, 2)


async def _fetch_rss_articles(client: httpx.AsyncClient, feed_url: str) -> list[dict]:
    """Parsea un RSS feed y retorna lista de artículos {title, description, pubDate}."""
    try:
        resp = await client.get(feed_url, follow_redirects=True)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        articles = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            link = (item.findtext("link") or "").strip()
            articles.append({"title": title, "description": desc, "pubDate": pub, "url": link})
        return articles
    except Exception:
        return []


async def fetch_news(currency: str, api_key: str = "") -> NewsSummary:
    """Busca noticias del ticker en múltiples RSS feeds de crypto."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        import asyncio
        all_articles = []
        results = await asyncio.gather(*[_fetch_rss_articles(client, url) for url in RSS_FEEDS])
        for articles in results:
            all_articles.extend(articles)

    keyword = currency.upper()
    relevant = []
    for article in all_articles:
        combined = (article["title"] + " " + article["description"]).upper()
        if keyword in combined:
            sentiment = _detect_sentiment(article["title"] + " " + article["description"])
            relevant.append(NewsItem(
                title=article["title"],
                source=article["url"].split("/")[2] if article["url"] else "",
                published_at=article["pubDate"],
                url=article["url"],
                votes_positive=0,
                votes_negative=0,
                sentiment=sentiment,
            ))
        if len(relevant) >= 10:
            break

    bullish = sum(1 for i in relevant if i.sentiment == "bullish")
    bearish = sum(1 for i in relevant if i.sentiment == "bearish")
    neutral = len(relevant) - bullish - bearish

    return NewsSummary(
        symbol=currency,
        items=relevant,
        bullish_count=bullish,
        bearish_count=bearish,
        neutral_count=neutral,
        sentiment_score=_sentiment_score(bullish, bearish, neutral),
    )


async def fetch_news_multiple(currencies: list[str], api_key: str = "") -> list[NewsSummary]:
    import asyncio
    tasks = [fetch_news(c, api_key) for c in currencies]
    return await asyncio.gather(*tasks)
