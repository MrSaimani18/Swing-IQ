import pandas as pd
import os
import re

MIN_ROWS_REQUIRED = 60


def load_stock_from_csv(file_path):
    """
    Stable adapter.
    Supports legacy CSVs where date is stored in `Price`.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("CSV file is empty")

    # -------------------------------------------------
    # DATE EXTRACTION
    # -------------------------------------------------
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    elif "Price" in df.columns:
        df = df[df["Price"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")]
        df = df.rename(columns={"Price": "Date"})
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    elif "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Date"})
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    else:
        raise ValueError("CSV schema invalid. Date column not found")

    df = df.dropna(subset=["Date"]).sort_values("Date")

    # -------------------------------------------------
    # NUMERIC CLEANING
    # -------------------------------------------------
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols).reset_index(drop=True)

    if len(df) < MIN_ROWS_REQUIRED:
        raise ValueError(
            f"Not enough data rows ({len(df)}). Minimum required: {MIN_ROWS_REQUIRED}"
        )

    # -------------------------------------------------
    # INDICATORS
    # -------------------------------------------------
    df["DMA_20"] = df["Close"].rolling(20).mean()
    df["DMA_50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean().replace(0, pd.NA)

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["AVG_VOL_20"] = df["Volume"].rolling(20).mean()

    df = df.dropna().reset_index(drop=True)

    if df.empty:
        raise ValueError("Indicators could not be computed")

    latest = df.iloc[-1]

    return {
        "symbol": os.path.basename(file_path).replace("_NS.csv", ""),
        "close": float(latest["Close"]),
        "dma_20": float(latest["DMA_20"]),
        "dma_50": float(latest["DMA_50"]),
        "rsi": float(latest["RSI"]),
        "volume": int(latest["Volume"]),
        "avg_volume": int(latest["AVG_VOL_20"]),
        "latest_date": str(latest["Date"].date()),
    }
