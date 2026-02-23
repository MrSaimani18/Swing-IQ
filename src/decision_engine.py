# src/decision_engine.py
import os
from typing import Dict, Any, List
from src.config import CONFIG

print("ENGINE FILE:", os.path.abspath(__file__))
print("🔥🔥🔥 DECISION ENGINE LOADED 🔥🔥🔥")


def _final(decision: str, reasons: List[str], trace: List[Dict[str, Any]], latest: Dict[str, Any]):
    return {
        "decision": decision,
        "reasons": reasons,
        "trace": trace,
        "engine_observability": {
            "engine_decision": decision,
            "engine_reasons": reasons.copy(),
            "rules_evaluated": len(trace),
            "latest_snapshot": latest
        }
    }


def make_decision(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    latest = stock_data["latest"]
    style = stock_data["style"]  # ✅ ALREADY UPPERCASE

    rsi = latest["rsi"]
    volume = latest["volume"]
    avg_volume = latest["avg_volume"]
    trend = latest["trend"]

    print(
        f"[DEBUG] {stock_data['symbol']} | "
        f"trend={trend}, rsi={rsi:.2f}, "
        f"vol={volume}, avg_vol={avg_volume}, "
        f"style={style}"
    )

    reasons = []
    trace = []

    # ───────── HARD RULE: TREND ─────────
    trace.append({
        "rule": "TREND_DIRECTION",
        "type": "HARD",
        "value": trend,
        "result": "PASS" if trend == "UP" else "FAIL"
    })

    if trend != "UP":
        reasons.append("Stock is not in an uptrend")
        return _final("NO TRADE", reasons, trace, latest)

    # ───────── HARD RULE: RSI EXTREMES ─────────
    if rsi < 20 or rsi > 80:
        trace.append({
            "rule": "RSI_EXTREMES",
            "type": "HARD",
            "value": rsi,
            "result": "FAIL"
        })
        reasons.append("RSI is in extreme zone")
        return _final("NO TRADE", reasons, trace, latest)

    # ───────── HARD RULE: DISTRIBUTION ─────────
    trace.append({
        "rule": "DISTRIBUTION_VOLUME",
        "type": "HARD",
        "value": {"volume": volume, "avg_volume": avg_volume},
        "result": "PASS" if volume >= avg_volume else "FAIL"
    })

    if volume < avg_volume:
        reasons.append("Distribution detected (low volume)")
        return _final("NO TRADE", reasons, trace, latest)

    # ───────── SOFT RULE: CONFIG-DRIVEN RSI BAND ─────────
    rsi_low, rsi_high = CONFIG["RSI_BANDS"][style]

    trade_allowed = rsi_low <= rsi <= rsi_high

    trace.append({
        "rule": "STYLE_RSI_BAND",
        "type": "SOFT",
        "style": style,
        "band": (rsi_low, rsi_high),
        "value": rsi,
        "result": "PASS" if trade_allowed else "FAIL"
    })

    if trade_allowed:
        reasons.append("All engine conditions satisfied")
        return _final("TRADE", reasons, trace, latest)

    reasons.append("Waiting for better RSI alignment")
    return _final("WAIT", reasons, trace, latest)
