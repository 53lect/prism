"""
Capa 5: Risk Layer — position sizing, fee-adjusted expected value, VaR simplificado.
"""

from ..config import ANALYSIS_FEE_RATE, MIN_PROFIT_FEE_MULTIPLIER


def analyze(market: dict, capital: float = 500.0, leverage: float = 3.0) -> dict:
    volatility = market.get("volatility", 0.5)      # std dev retornos 1h en %
    liquidity_score = market.get("liquidity_score", 1.0)

    # Fee round trip (entrada + salida)
    fee_round_trip_pct = ANALYSIS_FEE_RATE * 2 * leverage * 100  # como % del capital

    # Break-even: movimiento mínimo para cubrir fees
    fee_breakeven_pct = fee_round_trip_pct

    # Expected move en 4h (estimado como 2x std dev de 1h)
    expected_move_pct = volatility * 2

    # Expected Value simplificado (win rate 50% asumido conservador)
    win_rate = 0.50
    reward = expected_move_pct
    risk = expected_move_pct  # stop simétrico
    ev = (win_rate * reward) - ((1 - win_rate) * risk) - fee_round_trip_pct

    # Position sizing: Kelly simplificado con cap conservador
    # Máximo 5% del capital, reducido por liquidez baja
    liquidity_factor = min(liquidity_score / 100, 1.0)
    base_position_pct = 5.0
    position_size_pct = round(base_position_pct * liquidity_factor, 1)
    position_size_pct = max(1.0, min(position_size_pct, 5.0))

    # VaR simplificado: pérdida máxima probable al 95% (1.65 std devs)
    var_pct = volatility * 1.65 * leverage

    # Risk score: 0 (muy riesgoso) a 100 (seguro)
    risk_score = max(0, min(100, 100 - (var_pct * 10) + (liquidity_score * 0.3)))

    # Señal válida solo si EV > threshold
    valid = ev > (fee_round_trip_pct * (MIN_PROFIT_FEE_MULTIPLIER - 1))

    return {
        "capital": capital,
        "leverage": leverage,
        "position_size_pct": position_size_pct,
        "position_size_usd": round(capital * position_size_pct / 100 * leverage, 2),
        "fee_breakeven_pct": round(fee_breakeven_pct, 4),
        "expected_move_pct": round(expected_move_pct, 3),
        "expected_value": round(ev, 4),
        "var_95_pct": round(var_pct, 3),
        "risk_score": round(risk_score, 1),
        "valid": valid,
        "stop_loss_pct": round(volatility * 1.5, 3),
        "take_profit_pct": round(volatility * 3, 3),
    }
