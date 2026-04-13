"""
Modelos de base de datos SQLite para Prism.
Almacena análisis, señales e historial de pares.
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime, timezone
import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prism.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class PairAnalysis(Base):
    """Resultado completo de un análisis de 6 capas para un par."""
    __tablename__ = "pair_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Capa 1: Market data
    price = Column(Float)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    rsi_14 = Column(Float)
    volatility = Column(Float)
    funding_rate = Column(Float)
    open_interest = Column(Float)

    # Capa 2: Sentimiento
    fear_greed_index = Column(Float)
    fear_greed_label = Column(String(20))
    sentiment_score = Column(Float)

    # Capa 3: Noticias
    news_count = Column(Integer)
    news_sentiment_score = Column(Float)
    news_summary = Column(Text)

    # Capa 4: Macro
    btc_dominance = Column(Float)
    market_trend = Column(String(20))

    # Capa 5: Risk
    position_size_pct = Column(Float)   # % del capital recomendado
    fee_breakeven_pct = Column(Float)   # movimiento mínimo para cubrir fees
    expected_value = Column(Float)      # EV ajustado a fees
    risk_score = Column(Float)          # 0-100

    # Capa 6: Síntesis
    signal = Column(String(10))         # "LONG" | "SHORT" | "NEUTRAL"
    confidence = Column(Float)          # 0-100
    reasoning = Column(Text)
    stop_loss_pct = Column(Float)
    take_profit_pct = Column(Float)
    valid = Column(Boolean, default=True)  # False si EV < 2x fees


def init_db():
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
