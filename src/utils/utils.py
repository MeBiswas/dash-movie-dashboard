# src/utils/utils.py

def human_format(num):
    try:
        num = float(num)
    except:
        return "N/A"
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000.0:
            return f"{num:.2f}{unit}"
        num /= 1000.0
    return f"{num:.2f}P"