"""
GET /klines/{symbol} — datos de velas desde Binance para gráficos.
"""

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/klines", tags=["klines"])

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d"}
BINANCE_FUTURES = "https://fapi.binance.com/fapi/v1/klines"


@router.get("/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query("1h", description="Temporalidad: 15m, 1h, 4h, 1d"),
    limit: int = Query(100, ge=10, le=500),
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Intervalo inválido. Opciones: {sorted(VALID_INTERVALS)}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(BINANCE_FUTURES, params={
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit,
            })
            resp.raise_for_status()
            raw = resp.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error al obtener datos de Binance: {e}")

    return [
        {
            "time": int(k[0]) // 1000,  # timestamp en segundos (para lightweight-charts)
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        }
        for k in raw
    ]
