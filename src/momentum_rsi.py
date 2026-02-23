import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_NAME = "ICICIBANK_NS.csv"   # change stock if needed
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# -----------------------------
# LOAD & CLEAN DATA (reuse logic)
# -----------------------------
df = pd.read_csv(FILE_PATH)

df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]
df = df.rename(columns={"Price": "Date"})

numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").dropna()

# -----------------------------
# RSI CALCULATION
# -----------------------------
window = 14

delta = df["Close"].diff()
gain = delta.where(delta > 0, 0.0)
loss = -delta.where(delta < 0, 0.0)

avg_gain = gain.rolling(window=window).mean()
avg_loss = loss.rolling(window=window).mean()

rs = avg_gain / avg_loss
df["RSI"] = 100 - (100 / (1 + rs))

latest = df.iloc[-1]

print("\n📊 RSI ANALYSIS")
print("-------------------------")
print(f"Date       : {latest['Date'].date()}")
print(f"Close Price: {latest['Close']:.2f}")
print(f"RSI (14)   : {latest['RSI']:.2f}")

# -----------------------------
# RSI INTERPRETATION
# -----------------------------
if latest["RSI"] > 70:
    status = "OVERBOUGHT ❌ (avoid new buys)"
elif latest["RSI"] >= 60:
    status = "STRONG MOMENTUM 🔥 (ideal for swing)"
elif latest["RSI"] >= 40:
    status = "HEALTHY ZONE ✅"
elif latest["RSI"] >= 30:
    status = "WEAK / PULLBACK ⚠️"
else:
    status = "OVERSOLD 🧨 (risky, watch for reversal)"

print("\n📈 Momentum Status:", status)
