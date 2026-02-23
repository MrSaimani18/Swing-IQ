from src.config import CONFIG
from src.validator import validate_config
from src.logger import log_decision, log_scan_metadata
from src.services.decision_service import get_trade_decision
from src.data_adapter import load_stock_from_csv

import pandas as pd
from datetime import datetime
import os

# ---------------- VALIDATION ----------------
errors = validate_config()
if errors:
    print("❌ CONFIGURATION ERROR")
    for e in errors:
        print("-", e)
    exit(1)

# ---------------- CONFIG ----------------
STYLE = CONFIG["STYLE"]
TOP_N = CONFIG["TOP_N"]
STOCK_LIST_PATH = "stocks_list.csv"

# ---------------- LOAD STOCK UNIVERSE ----------------
def load_stock_universe():
    if not os.path.exists(STOCK_LIST_PATH):
        raise FileNotFoundError("stocks_list.csv not found")

    df = pd.read_csv(STOCK_LIST_PATH)
    symbols = (
        df["symbol"]
        .astype(str)
        .str.replace(".NS", "", regex=False)
        .tolist()
    )
    return symbols


# ---------------- MAIN PIPELINE ----------------
def run_smartswing():
    print("\n🚀 SMARTSWING — DAILY MARKET SCAN")
    print("=" * 55)

    stock_list = load_stock_universe()
    # stock_list = ["INFY", "AXISBANK"]

    total_symbols = len(stock_list)

    print(f"🔍 Scanning {total_symbols} stocks")
    print(f"🎯 ACTIVE STYLE: {STYLE}\n")

    # 🔒 ALWAYS WRITE METADATA FIRST
    log_scan_metadata(
        style=STYLE,
        total_symbols=total_symbols
    )

    scanned = 0

    for symbol in stock_list[:TOP_N]:
        scanned += 1

        try:
            # ---------------- LOAD DATA ----------------
            stock_data = load_stock_from_csv(
                file_path=f"data/{symbol}_NS.csv"
            )

            # ---------------- ENGINE DECISION ----------------
            result = get_trade_decision(stock_data)

        except Exception as e:
            # HARD FAIL → LOG AS NO TRADE
            result = {
                "decision": "NO TRADE",
                "reason": [f"Data load failed: {e}"],
                "trace": [],
                "entry": None,
                "stop": None,
                "target": None,
                "qty": None,
                "holding": None,
                "style": STYLE
            }

        # ---------------- LOG (SINGLE SOURCE OF TRUTH) ----------------
        log_decision(
            symbol=symbol,
            result=result
        )

        # ---------------- CONSOLE FEEDBACK ----------------
        print(f"📌 {symbol:12} → {result['decision']}")

    print("\n✅ Scan completed")
    print(f"📊 Symbols scanned: {scanned}")
    print("=" * 55)


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    run_smartswing()
