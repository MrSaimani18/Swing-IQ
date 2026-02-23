# =================================================
# BOOTSTRAP (MUST BE FIRST)
# =================================================
import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Optional debug (safe to keep for now)
print("✅ PROJECT_ROOT:", PROJECT_ROOT)
print("✅ sys.path (head):", sys.path[:3])

# =================================================
# STANDARD IMPORTS
# =================================================
import streamlit as st
import json
import math
import pandas as pd
import matplotlib.pyplot as plt

from src.data_adapter import load_stock_from_csv

# =================================================
# 🔎 DEBUG — ENV CHECK
# =================================================
st.write("📂 Streamlit CWD:", os.getcwd())
st.write("📁 Logs folder exists:", os.path.exists("logs"))

# =================================================
# PAGE SETUP
# =================================================
st.set_page_config(page_title="SmartSwing", layout="wide")

st.title("🚀 SmartSwing — Trade Dashboard")
st.caption("Batch-scanned, engine-verified trade intelligence")

st.markdown(
    "> **Philosophy:** Capital protection first. "
    "TRADE signals are rare by design. WAIT indicates setups forming."
)

st.divider()

# =================================================
# LOAD LATEST SCAN FILE
# =================================================
def load_latest_scan():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return None, []

    files = sorted(
        [f for f in os.listdir(log_dir) if f.startswith("scan_")],
        reverse=True
    )

    if not files:
        return None, []

    latest_file = os.path.join(log_dir, files[0])
    st.success(f"✅ Using scan file: {latest_file}")

    meta = None
    records = []

    with open(latest_file, "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("type") == "SCAN_META":
                meta = obj
            elif obj.get("type") == "DECISION":
                records.append(obj)

    st.info(f"📊 Total decisions loaded: {len(records)}")
    return meta, records


scan_meta, scan_results = load_latest_scan()

if not scan_results:
    st.warning("⚠️ No scan data found. Run `python3 -m src.smartswing` first.")
    st.stop()

# =================================================
# SCAN HEADER
# =================================================
if scan_meta:
    st.info(
        f"📄 Scan Time: **{scan_meta.get('scan_time')}** | "
        f"Style: **{scan_meta.get('style')}** | "
        f"Symbols: **{scan_meta.get('total_symbols')}**"
    )

# =================================================
# SPLIT RESULTS
# =================================================
trade_results = [r for r in scan_results if r["decision"] == "TRADE"]
wait_results = [r for r in scan_results if r["decision"] == "WAIT"]

st.success(f"🟢 TRADE count: {len(trade_results)}")
st.warning(f"🟡 WAIT count: {len(wait_results)}")

# =================================================
# 🔍 RULE TRACE RENDERER
# =================================================
def render_rule_trace(trace):
    for step in trace:
        rule = step.get("rule")
        result = step.get("result")
        rule_type = step.get("type", "")
        badge = "🟢 PASS" if result == "PASS" else "🔴 FAIL"

        if rule == "STYLE_RSI_BAND":
            low, high = step.get("band", [None, None])
            st.markdown(
                f"📐 **RSI Rule ({step['style']})**  \n"
                f"- RSI Value: **{step['value']:.2f}**  \n"
                f"- Ideal Range: **{low}–{high}**  \n"
                f"- Type: `{rule_type}` → {badge}"
            )
        else:
            st.markdown(f"✅ **{rule}** ({rule_type}) → {badge}")

# =================================================
# 📊 CHART BUILDER (ENGINE-ALIGNED)
# =================================================
@st.cache_data(show_spinner=False, ttl=60)
def build_chart_dataframe(symbol):
    path = f"data/{symbol}_NS.csv"
    if not os.path.exists(path):
        return None, None

    # Engine adapter validation (trust gate)
    _ = load_stock_from_csv(path)

    df = pd.read_csv(path)

    if "Price" in df.columns:
        df = df[df["Price"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")]
        df = df.rename(columns={"Price": "Date"})

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Close", "High", "Low", "Open", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().sort_values("Date")

    df["DMA_20"] = df["Close"].rolling(20).mean()
    df["DMA_50"] = df["Close"].rolling(50).mean()
    df = df.dropna()

    latest = df.iloc[-1]
    meta = {
        "from": df["Date"].iloc[0].date(),
        "to": df["Date"].iloc[-1].date(),
        "latest_close": round(float(latest["Close"]), 2),
    }

    return df, meta


def plot_price_chart(df, meta):
    st.caption(
        f"📅 Data range: **{meta['from']} → {meta['to']}** | "
        f"🔔 Latest Close: **₹{meta['latest_close']}**"
    )

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    ax.plot(df["Date"], df["DMA_20"], label="20 DMA")
    ax.plot(df["Date"], df["DMA_50"], label="50 DMA")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# =================================================
# 📈 TRADE SECTION
# =================================================
st.subheader("📈 TRADE — Action Now")

if not trade_results:
    st.info("🛡️ No high-confidence trades today.")
else:
    rows = math.ceil(len(trade_results) / 3)
    idx = 0

    for _ in range(rows):
        cols = st.columns(3)
        for col in cols:
            if idx >= len(trade_results):
                break

            trade = trade_results[idx]
            idx += 1

            with col:
                st.success(f"📈 {trade['symbol']}")
                st.markdown("**Decision:** TRADE")

                st.markdown("**Trade Plan:**")
                st.markdown(f"- Entry: {trade['entry']}")
                st.markdown(f"- Stop: {trade['stop']}")
                st.markdown(f"- Target: {trade['target']}")
                st.markdown(f"- Qty: {trade['qty']}")
                st.markdown(f"- Holding: {trade['holding']}")

                with st.expander("🔍 Why this trade?"):
                    for r in trade.get("reason", []):
                        st.markdown(f"- {r}")
                    st.markdown("**Rule Trace:**")
                    render_rule_trace(trade.get("trace", []))

                with st.expander("📊 Price & Trend Chart"):
                    df, meta = build_chart_dataframe(trade["symbol"])
                    if df is not None:
                        plot_price_chart(df, meta)

# =================================================
# ⏳ WAIT SECTION
# =================================================
st.subheader("⏳ WAIT — Setups Forming")

rows = math.ceil(len(wait_results) / 3)
idx = 0

for _ in range(rows):
    cols = st.columns(3)
    for col in cols:
        if idx >= len(wait_results):
            break

        wait = wait_results[idx]
        idx += 1

        with col:
            st.warning(f"⏳ {wait['symbol']}")
            st.markdown("**Decision:** WAIT")

            st.markdown("**Why WAIT?**")
            for r in wait.get("reason", []):
                st.markdown(f"- {r}")

            with st.expander("🔍 Rule Trace"):
                render_rule_trace(wait.get("trace", []))

            with st.expander("📊 Price & Trend Chart"):
                df, meta = build_chart_dataframe(wait["symbol"])
                if df is not None:
                    plot_price_chart(df, meta)
