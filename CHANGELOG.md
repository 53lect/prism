# Changelog

All notable changes to Prism will be documented here.

Format: [Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`

## [0.2.0] - 2026-04-12

### Added
- Motor de análisis de 6 capas (Phase 2) totalmente funcional
- Layer 1: Market Data — precio, RSI-14, volatilidad, funding rate, open interest, liquidity score (Binance)
- Layer 2: Sentiment — Fear & Greed Index via alternative.me (gratuito, sin API key)
- Layer 3: News — RSS scraping de CoinDesk + CoinTelegraph con sentiment score
- Layer 4: Macro — BTC dominance y market trend via CoinGecko global (gratuito)
- Layer 5: Risk — position sizing, fee-adjusted EV, VaR 95%, stop/take profit sugeridos
- Layer 6: Synthesis — Claude Sonnet 4.6 genera señal JSON con cache (TTL 15min + threshold 0.5%)
- SQLite persistence via SQLAlchemy (PairAnalysis model)
- Pipeline orquestador en `main.py` con capas 1-4 en paralelo (asyncio.gather)

### Fixed
- TypeError en format_signal cuando stop_loss_pct/take_profit_pct retornan None desde síntesis

## [0.1.1] - 2026-04-12

### Added
- Research Agent CLI completo (Phase 1)
- Binance market fetcher con RSI, volatilidad, funding rate, open interest
- RSS news fetcher (CoinDesk + CoinTelegraph) con detección de sentimiento
- Síntesis via Claude Sonnet: ranking de pares con justificación
- Resultado: LINK, DOGE, AVAX seleccionados como pares volátiles

---

## [0.1.0] - 2026-04-12

### Added
- Setup inicial del proyecto
- Estructura de carpetas según Bedrock Python profile
- pyproject.toml con dependencias base
