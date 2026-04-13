# SPEC — Prism

> Documento de implementación. Define qué construir, en qué orden, y cómo verificar que está completo.
> Actualizar este archivo antes de cambiar el plan en código.

---

## Fase 1 — Research Agent (CLI) ✅

  T 1.1 — Binance market fetcher: precio, volumen, RSI-14, volatilidad, funding rate, open interest
  T 1.2 — Liquidity score: score 0-100 basado en volumen y spread
  T 1.3 — News fetcher: RSS scraping de CoinDesk + CoinTelegraph con sentiment score
  T 1.4 — Síntesis Claude: ranking de pares candidatos con justificación
  T 1.5 — CLI: script `research.py --pairs A,B,C` que corre el agente completo

### Checkpoint

  - CLI corre sin errores con lista de pares
  - Claude retorna ranking con justificación por par
  - Pares volátiles seleccionados y guardados en config.py

---

## Fase 2 — Analysis Engine (6 capas) ✅

  T 2.1 — SQLite schema: tabla PairAnalysis con todos los campos de las 6 capas
  T 2.2 — Layer 1 Market Data: wraper sobre research/market.py
  T 2.3 — Layer 2 Sentiment: Fear & Greed Index via alternative.me
  T 2.4 — Layer 3 News: wraper sobre research/news.py
  T 2.5 — Layer 4 Macro: BTC dominance y market trend via CoinGecko
  T 2.6 — Layer 5 Risk: position sizing, fee-adjusted EV, VaR 95%, stop/take profit
  T 2.7 — Layer 6 Synthesis: Claude Sonnet con cache TTL 15min + threshold 0.5%
  T 2.8 — Pipeline: orchestrador en main.py con capas 1-4 en paralelo

### Checkpoint

  - Pipeline corre end-to-end para un par (LINKUSDT)
  - Señal se imprime en terminal con todos los campos
  - Resultado se persiste en SQLite
  - Claude solo se llama una vez por análisis (verificar con logs)

---

## Fase 3 — Backend FastAPI

  T 3.1 — App skeleton: routing, middleware, CORS, configuración
  T 3.2 — POST /analyze/{pair} → dispara pipeline → retorna señal completa en JSON
  T 3.3 — GET /signals/history → historial de señales con filtros opcionales
  T 3.4 — GET /pairs → lista de pares activos con último estado conocido
  T 3.5 — WebSocket /ws/live → actualizaciones en tiempo real cada X minutos

### Checkpoint

  - API responde correctamente en Postman / curl
  - Señal completa retorna en JSON estructurado
  - WebSocket envía updates periódicos sin desconectarse

---

## Fase 4 — Frontend Next.js

  T 4.1 — Setup: Next.js + Tailwind, estructura de carpetas, conexión a API local
  T 4.2 — Dashboard: lista de pares con señal actual (LONG / SHORT / NEUTRAL) y confianza
  T 4.3 — Detail view: análisis completo por par con las 6 capas desglosadas
  T 4.4 — Historial: tabla de señales pasadas con filtro por par y fecha
  T 4.5 — WebSocket: actualizaciones en vivo sin recargar la página

### Checkpoint

  - Dashboard muestra todos los pares configurados
  - Señales se actualizan en tiempo real via WebSocket
  - Detail view muestra todas las capas del análisis
  - Historial es consultable y legible
