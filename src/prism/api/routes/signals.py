"""
GET /signals/history — historial de señales persistidas en SQLite.
"""

from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from ...db.models import get_session, PairAnalysis

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/history")
def history(
    pair: str | None = Query(None, description="Filtrar por par, e.g. BTCUSDT"),
    limit: int = Query(50, ge=1, le=500),
):
    with get_session() as session:
        q = select(PairAnalysis).order_by(desc(PairAnalysis.analyzed_at)).limit(limit)
        if pair:
            q = q.where(PairAnalysis.symbol == pair.upper())

        rows = session.execute(q).scalars().all()

    return [
        {
            "id": r.id,
            "symbol": r.symbol,
            "analyzed_at": r.analyzed_at,
            "signal": r.signal,
            "confidence": r.confidence,
            "price": r.price,
            "rsi_14": r.rsi_14,
            "expected_value": r.expected_value,
            "risk_score": r.risk_score,
            "stop_loss_pct": r.stop_loss_pct,
            "take_profit_pct": r.take_profit_pct,
            "reasoning": r.reasoning,
            "valid": r.valid,
        }
        for r in rows
    ]
