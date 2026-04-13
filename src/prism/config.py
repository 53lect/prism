from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ANALYSIS_FEE_RATE = float(os.getenv("ANALYSIS_FEE_RATE", "0.0004"))
MIN_PROFIT_FEE_MULTIPLIER = float(os.getenv("MIN_PROFIT_FEE_MULTIPLIER", "2.0"))

# Pares de trading configurados
STABLE_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
VOLATILE_PAIRS: list[str] = ["LINKUSDT", "DOGEUSDT", "AVAXUSDT"]  # seleccionados por Research Agent 2026-04-12

ALL_PAIRS = STABLE_PAIRS + VOLATILE_PAIRS
