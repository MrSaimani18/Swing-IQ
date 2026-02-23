import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

results = []

for file in os.listdir(DATA_DIR):
    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(DATA_DIR, file)
    df = pd.read_csv(file_path)

    # ---------------- CLEAN DATA ----------------
    df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]
    df = df.rename(columns={"Price": "Date"})

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").dropna()

    if len(df) < 60:
        continue

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

    df["AVG_VOL_20"] = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]

    score = 0

    # ---------------- SCORING ----------------
    if latest["Close"] > latest["DMA_20"] > latest["DMA_50"]:
        score += 40

    if 35 <= latest["RSI"] <= 60:
        score += 25

    if abs(latest["Close"] - latest["DMA_20"]) / latest["Close"] < 0.02:
        score += 20

    if latest["Volume"] < latest["AVG_VOL_20"]:
        score += 15

    results.append({
        "Stock": file.replace("_NS.csv", ""),
        "Score": score,
        "Close": round(latest["Close"], 2),
        "RSI": round(latest["RSI"], 2)
    })

# ---------------- RESULTS ----------------
ranked = pd.DataFrame(results).sort_values("Score", ascending=False)

print("\n🏆 SMARTSWING STOCK RANKINGS")
print("-----------------------------")
print(ranked.head(5))
