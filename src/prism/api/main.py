"""
FastAPI app — entry point de la API de Prism.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analysis, signals, pairs, websocket, klines
from ..db.models import init_db

app = FastAPI(
    title="Prism API",
    description="Motor de análisis crypto con síntesis via Claude AI.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


app.include_router(analysis.router)
app.include_router(signals.router)
app.include_router(pairs.router)
app.include_router(websocket.router)
app.include_router(klines.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
