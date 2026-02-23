# src/config.py

# ==============================
# 🎯 TRADING STYLE
# ==============================
# Allowed values (case-insensitive input):
# "CONSERVATIVE", "NORMAL", "AGGRESSIVE"

DEBUG_ENGINE = True

# 👇 user / env input (can be any case)
RAW_STYLE = "NORMAL"

# 🔒 normalize ONCE
STYLE = RAW_STYLE.upper()


# ==============================
# 📊 RSI BANDS PER STYLE
# ==============================
RSI_BANDS = {
    "CONSERVATIVE": (40, 55),
    "NORMAL": (35, 65),
    "AGGRESSIVE": (30, 70),
}


# ==============================
# 📈 RISK : REWARD RATIO
# ==============================
RR = {
    "CONSERVATIVE": 2.0,
    "NORMAL": 2.5,
    "AGGRESSIVE": 3.0,
}


# ==============================
# ⏳ HOLDING PERIOD
# ==============================
HOLDING_PERIOD = {
    "CONSERVATIVE": "5–10 days",
    "NORMAL": "3–7 days",
    "AGGRESSIVE": "1–3 days",
}


# ==============================
# 💰 CAPITAL & RISK SETTINGS
# ==============================
CAPITAL = 10_000          # Total capital
RISK_PERCENT = 0.01       # 1% risk per trade


# ==============================
# 🔝 HOW MANY STOCKS TO SHOW
# ==============================
TOP_N = None


# ==============================
# 🧠 MASTER CONFIG OBJECT
# ==============================
CONFIG = {
    "STYLE": STYLE,                 # ✅ ALWAYS UPPERCASE
    "RSI_BANDS": RSI_BANDS,
    "RR": RR,
    "HOLDING_PERIOD": HOLDING_PERIOD,
    "CAPITAL": CAPITAL,
    "RISK_PERCENT": RISK_PERCENT,
    "TOP_N": TOP_N,
    "DEBUG_ENGINE": DEBUG_ENGINE,
}
