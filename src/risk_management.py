# src/risk_management.py

from src.config import CONFIG


def calculate_trade(entry: float):
    """
    Risk management engine.
    SINGLE SOURCE OF TRUTH for:
    - stop-loss
    - position sizing
    - target

    All downstream layers (service, logger, UI)
    must use values returned from here.
    """

    # -----------------------------
    # BASIC VALIDATION
    # -----------------------------
    if entry <= 0:
        raise ValueError("Invalid entry price")

    # -----------------------------
    # CONFIG LOAD (SAFE)
    # -----------------------------
    capital = CONFIG["CAPITAL"]
    risk_percent = CONFIG["RISK_PERCENT"]
    style = CONFIG["STYLE"]              # ALWAYS UPPERCASE
    rr = CONFIG["RR"][style]

    # -----------------------------
    # STOP-LOSS LOGIC (STYLE BASED)
    # -----------------------------
    # Conservative → wider stop
    # Normal       → medium stop
    # Aggressive   → tighter stop
    if style == "CONSERVATIVE":
        stop_pct = 0.03      # 3%
    elif style == "NORMAL":
        stop_pct = 0.02      # 2%
    else:  # AGGRESSIVE
        stop_pct = 0.015     # 1.5%

    stop = entry * (1 - stop_pct)

    risk_per_share = entry - stop
    if risk_per_share <= 0:
        raise ValueError("Invalid stop-loss calculation")

    # -----------------------------
    # POSITION SIZING
    # -----------------------------
    max_risk = capital * risk_percent
    qty = int(max_risk / risk_per_share)

    if qty <= 0:
        raise ValueError("Trade rejected: position size too small")

    # -----------------------------
    # TARGET CALCULATION
    # -----------------------------
    target = entry + (risk_per_share * rr)

    # -----------------------------
    # RETURN — AUTHORITATIVE TRADE PLAN
    # -----------------------------
    return {
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "target": round(target, 2),
        "qty": qty,

        # 🔍 audit / trust fields (NO logic impact)
        "stop_pct": stop_pct,
        "risk_per_share": round(risk_per_share, 2),
        "rr": rr,
        "style": style,
    }
