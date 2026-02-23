# src/services/decision_service.py

from src.config import CONFIG
from src.decision_engine import make_decision
from src.risk_management import calculate_trade
from src.data_adapter import load_stock_from_csv
import pandas as pd


def get_trade_decision(stock_data=None, symbol=None):
    """
    Service layer orchestrator.
    Adapts CSV data → engine contract.
    Engine logic remains untouched.
    """

    # -------------------------------------------------
    # 0️⃣ LOAD DATA
    # -------------------------------------------------
    if stock_data is None:
        if symbol is None:
            return {
                "stock": "UNKNOWN",
                "decision": "NO TRADE",
                "reason": ["No stock data or symbol provided"],
                "style": CONFIG["STYLE"]
            }

        try:
            stock_data = load_stock_from_csv(f"data/{symbol}_NS.csv")
        except Exception as e:
            return {
                "stock": symbol,
                "decision": "NO TRADE",
                "reason": [f"Data load failed: {str(e)}"],
                "style": CONFIG["STYLE"]
            }

    symbol = stock_data["symbol"]

    # -------------------------------------------------
    # 1️⃣ SANITY CHECK
    # -------------------------------------------------
    required = ["close", "dma_20", "dma_50", "rsi", "volume", "avg_volume"]
    for k in required:
        if k not in stock_data or pd.isna(stock_data[k]):
            return {
                "stock": symbol,
                "decision": "NO TRADE",
                "reason": [f"Invalid or missing value: {k}"],
                "style": CONFIG["STYLE"]
            }

    # -------------------------------------------------
    # 2️⃣ ENGINE CONTRACT (STRICT)
    # -------------------------------------------------
    engine_input = {
        "symbol": symbol,
        "close": stock_data["close"],
        "dma_20": stock_data["dma_20"],
        "dma_50": stock_data["dma_50"],
        "rsi": stock_data["rsi"],
        "volume": stock_data["volume"],
        "avg_volume": stock_data["avg_volume"],
        "latest": {
            "trend": "UP" if stock_data["close"] > stock_data["dma_50"] else "DOWN",
            "rsi": stock_data["rsi"],
            "volume": stock_data["volume"],
            "avg_volume": stock_data["avg_volume"]
        },
        "style": CONFIG["STYLE"]
    }

    engine_result = make_decision(engine_input)

    print(
        f"[ENGINE RESULT] {symbol} → "
        f"{engine_result['decision']} | "
        f"reasons={engine_result.get('reasons')} | "
        f"style={CONFIG['STYLE']}"
    )

    decision = engine_result["decision"]
    reasons = engine_result.get("reasons", [])
    trace = engine_result.get("trace", [])

    # -------------------------------------------------
    # 3️⃣ HONOR ENGINE DECISION FIRST
    # -------------------------------------------------
    if decision != "TRADE":
        return {
            "stock": symbol,
            "decision": decision,
            "reason": reasons,
            "trace": trace,
            "style": CONFIG["STYLE"]
        }

    # -------------------------------------------------
    # 4️⃣ RISK MANAGEMENT (SINGLE SOURCE OF TRUTH)
    # -------------------------------------------------
    try:
        trade = calculate_trade(entry=stock_data["close"])
    except Exception as e:
        return {
            "stock": symbol,
            "decision": "NO TRADE",
            "reason": reasons + [f"Risk rejected: {str(e)}"],
            "trace": trace + ["BLOCKED_BY_RISK"],
            "style": CONFIG["STYLE"]
        }

    # -------------------------------------------------
    # 5️⃣ FINAL RESPONSE
    # -------------------------------------------------
    return {
        "stock": symbol,
        "decision": "TRADE",
        "reason": reasons,
        "trace": trace,
        "entry": trade["entry"],
        "stop": trade["stop"],
        "target": trade["target"],
        "qty": trade["qty"],
        "holding": CONFIG["HOLDING_PERIOD"][CONFIG["STYLE"]],
        "style": CONFIG["STYLE"]
    }
