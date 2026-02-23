from src.config import CONFIG


def validate_config():
    errors = []

    # Capital
    if CONFIG["CAPITAL"] <= 0:
        errors.append("Capital must be greater than 0")

    # Risk percent
    if not (0 < CONFIG["RISK_PERCENT"] <= 0.03):
        errors.append("Risk percent should be between 0 and 3%")

    # TOP_N
    # if CONFIG["TOP_N"] <= 0 or CONFIG["TOP_N"] > 10:
    #     errors.append("TOP_N should be between 1 and 10")
    top_n = CONFIG.get("TOP_N")

    if top_n is not None:
        if not isinstance(top_n, int) or top_n <= 0:
            errors.append("TOP_N must be a positive integer or None")


    # Style
    valid_styles = CONFIG["RSI_BANDS"].keys()
    if CONFIG["STYLE"] not in valid_styles:
        errors.append(f"STYLE must be one of {list(valid_styles)}")

    # RSI bands
    for style, (low, high) in CONFIG["RSI_BANDS"].items():
        if low >= high:
            errors.append(f"Invalid RSI band for {style}: low >= high")

    # Risk–Reward
    for style, rr in CONFIG["RR"].items():
        if rr < 1.2:
            errors.append(f"RR too low for {style} (must be ≥ 1.2)")

    return errors
