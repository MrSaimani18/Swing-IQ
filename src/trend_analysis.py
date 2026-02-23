import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_NAME = "ICICIBANK_NS.csv"   # you can change stock later
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# Load cleaned data
df = pd.read_csv(FILE_PATH)

# -----------------------------
# CLEAN DATA (reuse Day 2 logic)
# -----------------------------
df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]
df = df.rename(columns={"Price": "Date"})

numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").dropna()

# -----------------------------
# TREND LOGIC
# -----------------------------
df["DMA_20"] = df["Close"].rolling(window=20).mean()
df["DMA_50"] = df["Close"].rolling(window=50).mean()

latest = df.iloc[-1]

print("\n📈 TREND ANALYSIS")
print("-------------------------")
print(f"Date        : {latest['Date'].date()}")
print(f"Close Price : {latest['Close']:.2f}")
print(f"20 DMA      : {latest['DMA_20']:.2f}")
print(f"50 DMA      : {latest['DMA_50']:.2f}")

# -----------------------------
# TREND DECISION
# -----------------------------
if latest["Close"] > latest["DMA_20"] > latest["DMA_50"]:
    trend = "STRONG UPTREND 🔥"
elif latest["Close"] > latest["DMA_20"]:
    trend = "WEAK UPTREND ⚠️"
elif latest["Close"] < latest["DMA_20"] < latest["DMA_50"]:
    trend = "DOWNTREND ❌"
else:
    trend = "SIDEWAYS 🤷‍♂️"

print("\n📊 Trend Status:", trend)
