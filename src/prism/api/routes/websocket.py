"""
WebSocket /ws/live — envía análisis actualizados de todos los pares cada X minutos.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...main import analyze_pair, save_analysis
from ...config import ALL_PAIRS

router = APIRouter(tags=["websocket"])

UPDATE_INTERVAL_SECONDS = 300  # 5 minutos


@router.websocket("/ws/live")
async def live(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            results = []
            for symbol in ALL_PAIRS:
                result = await analyze_pair(symbol)
                save_analysis(result)
                syn = result["synthesis"]
                results.append({
                    "symbol": symbol,
                    "signal": syn.get("signal"),
                    "confidence": syn.get("confidence"),
                    "price": result["market"]["price"],
                    "from_cache": syn.get("from_cache", False),
                })

            await websocket.send_text(json.dumps(results))
            await asyncio.sleep(UPDATE_INTERVAL_SECONDS)

    except WebSocketDisconnect:
        pass
