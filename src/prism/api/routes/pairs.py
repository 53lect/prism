"""
GET /pairs — lista de pares activos con el último análisis conocido.
"""

from fastapi import APIRouter
from sqlalchemy import select, desc
from ...db.models import get_session, PairAnalysis
from ...config import ALL_PAIRS

router = APIRouter(prefix="/pairs", tags=["pairs"])


@router.get("/")
def list_pairs():
    with get_session() as session:
        results = []
        for symbol in ALL_PAIRS:
            row = session.execute(
                select(PairAnalysis)
                .where(PairAnalysis.symbol == symbol)
                .order_by(desc(PairAnalysis.analyzed_at))
                .limit(1)
            ).scalar_one_or_none()

            results.append({
                "symbol": symbol,
                "last_signal": row.signal if row else None,
                "last_confidence": row.confidence if row else None,
                "last_price": row.price if row else None,
                "last_analyzed_at": row.analyzed_at if row else None,
                "valid": row.valid if row else None,
            })

    return results
