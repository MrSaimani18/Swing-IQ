import os
import json
from datetime import datetime

print("LOGGER CWD:", os.getcwd())


# -------------------------------------------------
# LOG DIRECTORY
# -------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# -------------------------------------------------
# CREATE UNIQUE LOG FILE PER SCAN
# -------------------------------------------------
SCAN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
SCAN_LOG_FILE = os.path.join(LOG_DIR, f"scan_{SCAN_TIMESTAMP}.jsonl")

# -------------------------------------------------
# INTERNAL: JSON SAFETY
# -------------------------------------------------
def _json_safe(value):
    """
    Ensures any value is JSON serializable.
    Converts unsupported objects to string.
    Logger must NEVER crash.
    """
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)

# -------------------------------------------------
# SCAN METADATA (MUST BE FIRST LINE)
# -------------------------------------------------
def log_scan_metadata(style, total_symbols):
    """
    Writes scan-level metadata.
    MUST be called ONCE before logging any decisions.
    """
    meta = {
        "type": "SCAN_META",
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style": _json_safe(style),
        "total_symbols": int(total_symbols),
        "scan_id": SCAN_TIMESTAMP
    }

    # Overwrite file to guarantee clean scan
    with open(SCAN_LOG_FILE, "w") as f:
        f.write(json.dumps(meta) + "\n")

# -------------------------------------------------
# LOG PER-STOCK DECISION
# -------------------------------------------------
def log_decision(symbol, result):
    """
    Appends ONE stock decision as ONE JSON line.
    Hardened against non-JSON objects.
    """
    if not result or not isinstance(result, dict):
        return  # safety guard

    # -----------------------------
    # TRACE SANITIZATION (CRITICAL)
    # -----------------------------
    raw_trace = result.get("trace", [])
    safe_trace = []

    for step in raw_trace:
        if isinstance(step, dict):
            safe_trace.append(
                {k: _json_safe(v) for k, v in step.items()}
            )
        else:
            safe_trace.append(_json_safe(step))

    record = {
        "type": "DECISION",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": _json_safe(symbol),
        "decision": _json_safe(result.get("decision")),
        "reason": [_json_safe(r) for r in result.get("reason", [])],
        "trace": safe_trace,
        "entry": _json_safe(result.get("entry")),
        "stop": _json_safe(result.get("stop")),
        "target": _json_safe(result.get("target")),
        "qty": _json_safe(result.get("qty")),
        "holding": _json_safe(result.get("holding")),
        "style": _json_safe(result.get("style")),
    }

    with open(SCAN_LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

# -------------------------------------------------
# OPTIONAL: LOAD LATEST SCAN FILE
# -------------------------------------------------
def load_latest_scan_file():
    """
    Returns path to latest scan log file.
    """
    files = sorted(
        [f for f in os.listdir(LOG_DIR) if f.startswith("scan_")],
        reverse=True
    )
    return os.path.join(LOG_DIR, files[0]) if files else None
