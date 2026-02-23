import pandas as pd
import yfinance as yf
import os
import time

# -----------------------------
# Path setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STOCK_LIST_PATH = os.path.join(BASE_DIR, "stocks_list.csv")

# Create data folder if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# Read stock list
# -----------------------------
stocks_df = pd.read_csv(STOCK_LIST_PATH)
stocks = stocks_df["symbol"].tolist()

print(f"\n📈 Reading market data for {len(stocks)} stocks...\n")

# -----------------------------
# Fetch data for each stock
# -----------------------------
for stock in stocks:
    try:
        print(f"Fetching {stock} ...")

        data = yf.download(
            stock,
            period="1y",
            interval="1d",
            progress=False
        )

        if data.empty:
            print(f"⚠️ No data found for {stock}")
            continue

        file_name = stock.replace(".", "_") + ".csv"
        file_path = os.path.join(DATA_DIR, file_name)

        data.to_csv(file_path)

        print(f"✅ Saved data → data/{file_name}")

        # Pause to avoid API rate limits
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error fetching {stock}: {e}")

print("\n✅ Market data fetching completed.\n")
