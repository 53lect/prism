# Prism

> Motor de análisis de mercado crypto con síntesis via Claude AI.

## What it does

Prism analiza pares de trading crypto en Binance usando 6 capas de análisis confluente (datos de mercado, sentimiento, noticias, macro, riesgo, y síntesis AI) para generar señales direccionales con recomendación de position sizing ajustada a fees.

## Requirements

- Python 3.11+
- uv (package manager)
- API key de Anthropic (Claude)

## Setup

```bash
git clone https://github.com/53lect/prism
cd prism

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## Usage

```bash
# Agente de investigación (selección de pares)
uv run python scripts/research.py --pairs DOGE PEPE AVAX LINK ARB

# Servidor de análisis (Phase 3+)
uv run uvicorn src.prism.api.main:app --reload
```

## Development

```bash
# Ejecutar tests
uv run pytest

# Lint y formato
uv run ruff check src/
uv run ruff format src/
```

## Architecture

```
Phase 1: Research Agent (CLI)     → selección de pares volátiles
Phase 2: Analysis Engine          → 6-layer pipeline por par
Phase 3: FastAPI Backend          → API REST + WebSocket
Phase 4: Next.js Frontend         → dashboard de señales
```

## Versioning

Semantic Versioning — ver [CHANGELOG.md](CHANGELOG.md)
