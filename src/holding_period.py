import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_NAME = "ICICIBANK_NS.csv"   # change if needed
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# ---------------- LOAD & CLEAN ----------------
df = pd.read_csv(FILE_PATH)
df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]
df = df.rename(columns={"Price": "Date"})

for col in ["Open", "High", "Low", "Close", "Volume"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").dropna()

# ---------------- INDICATORS ----------------
df["DMA_20"] = df["Close"].rolling(20).mean()
df["DMA_50"] = df["Close"].rolling(50).mean()

delta = df["Close"].diff()
gain = delta.where(delta > 0, 0.0)
loss = -delta.where(delta < 0, 0.0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
df["RSI"] = 100 - (100 / (1 + rs))

# Volatility (Average Daily Range %)
df["RangePct"] = (df["High"] - df["Low"]) / df["Close"] * 100
avg_range = df["RangePct"].rolling(10).mean().iloc[-1]

latest = df.iloc[-1]

# ---------------- VOLATILITY BUCKET ----------------
# thresholds are adjustable later (tweak empirically)
if avg_range < 1.5:
    vol_bucket = "LOW"
elif avg_range > 2.5:
    vol_bucket = "HIGH"
else:
    vol_bucket = "NORMAL"

# ---------------- HOLDING LOGIC (corrected) ----------------
holding = "WAIT"
reasons = []

# Must be in bullish trend to consider
is_bullish = latest["Close"] > latest["DMA_20"] > latest["DMA_50"]

rsi = latest["RSI"]

if not is_bullish:
    holding = "NO TRADE"
    reasons.append("Trend not bullish")
elif rsi > 65:
    holding = "NO TRADE"
    reasons.append("RSI too high (late stage)")
else:
    # Early stage RSI
    if 35 <= rsi <= 45:
        if vol_bucket == "LOW":
            holding = "HOLD 5-10 days"
            reasons.append("Early stage + low volatility => give time")
        elif vol_bucket == "NORMAL":
            holding = "HOLD 4-7 days"
            reasons.append("Early stage + normal volatility")
        else:  # HIGH
            holding = "HOLD 2-4 days"
            reasons.append("Early stage + high volatility => move fast")
    # Middle stage RSI
    elif 45 < rsi <= 60:
        if vol_bucket == "LOW":
            holding = "HOLD 10-20 days"
            reasons.append("Middle stage + low volatility => longer hold")
        elif vol_bucket == "NORMAL":
            holding = "HOLD 7-12 days"
            reasons.append("Middle stage + normal volatility")
        else:  # HIGH
            holding = "HOLD 4-7 days"
            reasons.append("Middle stage + high volatility => shorter hold")
    # RSI between 60 and 65 (approaching late)
    elif 60 < rsi <= 65:
        if vol_bucket == "LOW":
            holding = "HOLD 7-12 days (cautious)"
            reasons.append("Approaching late stage but low volatility")
        else:
            holding = "HOLD 3-7 days (cautious)"
            reasons.append("Approaching late stage; manage risk tightly")
    else:
        holding = "WAIT"
        reasons.append("RSI or conditions unclear")

# ---------------- OUTPUT ----------------
print("\n⏳ HOLDING PERIOD ESTIMATION (CORRECTED)")
print("----------------------------------------")
print(f"Close Price : {latest['Close']:.2f}")
print(f"RSI         : {rsi:.2f}")
print(f"Avg Range % : {avg_range:.2f}")
print(f"Vol bucket  : {vol_bucket}")
print("\n📌 Suggested Holding:", holding)
print("📝 Reasons:")
for r in reasons:
    print("-", r)
