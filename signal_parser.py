import re

def parse_signal(message):
    data = {}
    message = message.lower()
    lines = message.splitlines()

    for line in lines:
        line = line.strip()

        # Side (LONG or SHORT)
        if "long" in line:
            data["side"] = "LONG"
        elif "short" in line:
            data["side"] = "SHORT"

        # Symbol
        if "#" in line and "/usdt" in line:
            symbol_raw = line.replace("#", "").replace("/", "").replace("usdt", "").strip().upper()
            data["symbol"] = symbol_raw + "USDT"

        # Entry zone
        if "entry" in line:
            entry_match = re.findall(r"([0-9.]+)", line)
            if entry_match:
                data["entry"] = float(entry_match[0])  # First price from entry zone

        # Stop Loss
        if "sl" in line or "stop" in line:
            sl_match = re.findall(r"([0-9.]+)", line)
            if sl_match:
                data["sl"] = float(sl_match[0])

        # Targets
        if "target" in line or "tp" in line:
            targets = re.findall(r"([0-9.]+)", line)
            if targets:
                data["tp"] = [float(t) for t in targets]

    return data
