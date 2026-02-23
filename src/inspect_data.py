import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_NAME = "ICICIBANK_NS.csv"   # change if needed
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

print("\n📊 Loading raw data...")
df = pd.read_csv(FILE_PATH)

print("\n--- Raw Head ---")
print(df.head(5))

# -----------------------------
# CLEANING STEP 1: Remove junk rows
# -----------------------------
# Keep only rows where Date looks like a date
df = df[df["Price"].str.contains(r"\d{4}-\d{2}-\d{2}", na=False)]

# Rename Price column to Date
df = df.rename(columns={"Price": "Date"})

# -----------------------------
# CLEANING STEP 2: Convert types
# -----------------------------
numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------
# CLEANING STEP 3: Date handling
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.dropna()

# -----------------------------
# FINAL INSPECTION
# -----------------------------
print("\n✅ CLEANED DATA SAMPLE")
print(df.head())

print("\n--- Data Info After Cleaning ---")
print(df.info())

print("\n--- Missing Values After Cleaning ---")
print(df.isnull().sum())

print("\n--- Basic Price Stats ---")
print(df[numeric_cols].describe())

print(f"\n✅ Final rows count: {len(df)}")
