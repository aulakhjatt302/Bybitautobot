import re

def parse_signal(message):
    message = message.upper()
    side = "LONG" if "LONG" in message else "SHORT"

    # Symbol
    match_symbol = re.search(r"#?([A-Z]+)[\/\-]USDT", message)
    symbol = match_symbol.group(1) + "USDT" if match_symbol else None

    # Entry zone
    match_entry = re.search(r"ENTRY.*?[:\-–]\s*([\d\.]+)(?:\s*[-TO]+\s*([\d\.]+))?", message)
    if match_entry:
        entry_from = float(match_entry.group(1))
        entry_to = float(match_entry.group(2)) if match_entry.group(2) else entry_from
    else:
        entry_from = entry_to = None

    # Stop loss
    match_sl = re.search(r"STOP ?LOSS.*?[:\-–]\s*([\d\.]+)", message)
    stop_loss = float(match_sl.group(1)) if match_sl else None

    # Targets (all numbers after "Target" or "TP")
    targets = [float(tp) for tp in re.findall(r"(?:TP\d*|TARGET\d*|🎯|🥇|🥈|🥉)[:\-–]?\s*\$?([\d\.]+)", message)]

    return {
        "symbol": symbol,
        "side": side,
        "entry": (entry_from + entry_to)/2 if entry_from and entry_to else None,
        "stop_loss": stop_loss,
        "targets": targets[:2]  # Only first 2 targets for trade exit logic
    }
