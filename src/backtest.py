import pandas as pd
import os
from src.config import CONFIG



def run_backtest(file_name):
    FILE_PATH = os.path.join("data", file_name)

    CAPITAL = CONFIG["CAPITAL"]
    RISK_PERCENT = CONFIG["RISK_PERCENT"]
    STYLE = CONFIG["STYLE"]

    rsi_low, rsi_high = CONFIG["RSI_BANDS"][STYLE]
    RR = CONFIG["RR"][STYLE]

    # -------- LOAD DATA --------
    df = pd.read_csv(FILE_PATH)

    df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]
    df = df.rename(columns={"Price": "Date"})

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().reset_index(drop=True)

    # -------- INDICATORS --------
    df["DMA_20"] = df["Close"].rolling(20).mean()
    df["DMA_50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df = df.dropna().reset_index(drop=True)

    # -------- BACKTEST STATE --------
    in_trade = False
    entry = stop = target = qty = 0
    trades = []

    # -------- BACKTEST LOOP --------
    for i in range(1, len(df)):
        row = df.iloc[i]

        if in_trade:
            if row["Low"] <= stop:
                trades.append((stop - entry) * qty)
                in_trade = False
            elif row["High"] >= target:
                trades.append((target - entry) * qty)
                in_trade = False
            continue

        bullish = row["Close"] > row["DMA_20"] > row["DMA_50"]
        rsi_ok = rsi_low <= row["RSI"] <= rsi_high

        if not bullish or not rsi_ok:
            continue

        entry = row["Close"]
        stop = row["DMA_50"]
        risk_per_share = entry - stop

        if risk_per_share <= 0:
            continue

        qty = int((CAPITAL * RISK_PERCENT) / risk_per_share)
        if qty <= 0:
            continue

        target = entry + (risk_per_share * RR)
        in_trade = True

    # -------- RESULTS --------
    total_trades = len(trades)
    wins = len([p for p in trades if p > 0])
    losses = len([p for p in trades if p <= 0])
    win_rate = (wins / total_trades * 100) if total_trades else 0
    net_pnl = sum(trades)
    avg_win = sum(p for p in trades if p > 0) / wins if wins else 0
    avg_loss = sum(p for p in trades if p <= 0) / losses if losses else 0

    return {
        "stock": file_name.replace("_NS.csv", ""),
        "trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "net_pnl": net_pnl,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }


# -------- MULTI-STOCK RUN --------
STOCK_FILES = [
    "ICICIBANK_NS.csv",
    "HDFCBANK_NS.csv",
    "RELIANCE_NS.csv",
    "TCS_NS.csv",
    "INFY_NS.csv"
]

results = []

for stock in STOCK_FILES:
    try:
        results.append(run_backtest(stock))
    except Exception as e:
        print(f"⚠️ Error in {stock}: {e}")


print("\n📊 MULTI-STOCK BACKTEST SUMMARY")
print("-" * 50)

df = pd.DataFrame(results)
print(df[["stock", "trades", "win_rate", "net_pnl"]])

print("\n📈 OVERALL PERFORMANCE")
print("-" * 50)
print(f"Total Trades : {df['trades'].sum()}")
print(f"Net P&L ₹    : {df['net_pnl'].sum():.2f}")
print(f"Avg Win Rate : {df['win_rate'].mean():.2f}%")
print(f"Style        : {CONFIG['STYLE']}")
