def explain_trade(stock, trend, rsi, volume_status, entry, stop, target, qty, holding):
    explanation = []

    explanation.append(f"📊 {stock} TRADE SUMMARY")
    explanation.append("-" * 40)

    # Trend
    explanation.append("🟢 Trend Analysis:")
    explanation.append(
        "The stock is in a bullish trend, with price trading above key moving averages."
        if trend else
        "The trend is not bullish, so new trades are avoided."
    )

    # RSI
    explanation.append("\n⏱ Momentum (RSI):")
    explanation.append(
        f"RSI is at {rsi}, indicating healthy momentum without being overbought."
        if 35 <= rsi <= 60 else
        f"RSI is at {rsi}, which suggests poor timing."
    )

    # Volume
    explanation.append("\n📦 Volume Check:")
    explanation.append(
        "Volume behavior supports the price move, indicating genuine participation."
        if volume_status == "HEALTHY" else
        "Volume does not strongly support this move."
    )

    # Risk
    explanation.append("\n🛡 Risk Management:")
    explanation.append(
        f"Entry is planned near ₹{entry}. If price falls below ₹{stop}, the trade idea becomes invalid."
    )

    # Target
    explanation.append("\n🎯 Reward Expectation:")
    explanation.append(
        f"The target is set near ₹{target}, offering a favorable risk–reward ratio."
    )

    # Quantity
    explanation.append("\n📐 Position Size:")
    explanation.append(
        f"Quantity is adjusted to {qty} shares to limit loss if the stop-loss is hit."
    )

    # Holding
    explanation.append("\n⏳ Holding Period:")
    explanation.append(
        f"This trade is expected to be held for {holding} based on trend strength and volatility."
    )

    explanation.append("\n✅ Overall, this trade follows disciplined rules and controlled risk.")

    return "\n".join(explanation)


# ---------------- SAMPLE RUN ----------------
if __name__ == "__main__":
    print(
        explain_trade(
            stock="ICICIBANK",
            trend=True,
            rsi=48,
            volume_status="HEALTHY",
            entry=1343,
            stop=1299,
            target=1410,
            qty=2,
            holding="5–10 days"
        )
    )
