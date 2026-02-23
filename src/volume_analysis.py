import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_NAME = "ICICIBANK_NS.csv"   # change stock if needed
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# -----------------------------
# LOAD & CLEAN DATA
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
# VOLUME ANALYSIS
# -----------------------------
df["AVG_VOLUME_20"] = df["Volume"].rolling(window=20).mean()

latest = df.iloc[-1]

print("\n📊 VOLUME ANALYSIS")
print("-------------------------")
print(f"Date          : {latest['Date'].date()}")
print(f"Close Price  : {latest['Close']:.2f}")
print(f"Volume       : {int(latest['Volume'])}")
print(f"20D Avg Vol  : {int(latest['AVG_VOLUME_20'])}")

# -----------------------------
# VOLUME INTERPRETATION
# -----------------------------
if latest["Volume"] > latest["AVG_VOLUME_20"] * 1.5:
    status = "HIGH VOLUME 🔥 (strong participation)"
elif latest["Volume"] < latest["AVG_VOLUME_20"] * 0.7:
    status = "LOW VOLUME 😴 (weak selling / pullback)"
else:
    status = "NORMAL VOLUME ⚖️"

print("\n📈 Volume Status:", status)

