# src/utils/formatting.py

def format_money(x):
    try:
        x = float(x)
        if abs(x) >= 1e9:
            return f"${x/1e9:.2f}B"
        if abs(x) >= 1e6:
            return f"${x/1e6:.2f}M"
        return f"${x:,.0f}"
    except:
        return "N/A"

def money_axis(x):
    if abs(x) >= 1e9:
        return f"{x/1e9:.1f}B"
    if abs(x) >= 1e6:
        return f"{x/1e6:.1f}M"
    return f"{x/1e3:.0f}K"
