"""
POST /analyze/{pair} — dispara el pipeline completo y retorna la señal.
"""

from fastapi import APIRouter, HTTPException
from ...main import analyze_pair, save_analysis
from ...config import ALL_PAIRS

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/{pair}")
async def analyze(pair: str, capital: float = 500.0, leverage: float = 3.0):
    symbol = pair.upper()
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"

    if symbol not in ALL_PAIRS:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} no está en la lista de pares configurados. Pares válidos: {ALL_PAIRS}",
        )

    result = await analyze_pair(symbol, capital=capital, leverage=leverage)
    save_analysis(result)
    return result
