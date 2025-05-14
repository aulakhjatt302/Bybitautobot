import re

def parse_signal(message):
    signal = {}

    # ✅ Symbol detection (e.g. #BOME/USDT)
    symbol_match = re.search(r'#?([A-Z0-9]{2,})[\/\-]?(USDT)', message, re.IGNORECASE)
    if symbol_match:
        signal['symbol'] = (symbol_match.group(1) + symbol_match.group(2)).upper()

    # ✅ Trade direction
    if 'short' in message.lower():
        signal['side'] = 'SELL'
    elif 'long' in message.lower():
        signal['side'] = 'BUY'

    # ✅ Entry price (single or range)
    entry_match = re.search(r'Entry[:=]?\s*\$?([\d.]+)(?:\s*-\s*\$?([\d.]+))?', message, re.IGNORECASE)
    if entry_match:
        if entry_match.group(2):
            entry_price = (float(entry_match.group(1)) + float(entry_match.group(2))) / 2
        else:
            entry_price = float(entry_match.group(1))
        signal['entry'] = round(entry_price, 6)

    # ✅ Stop loss
    sl_match = re.search(r'SL[:=]?\s*\$?([\d.]+)|Stop[- ]?loss[:=]?\s*\$?([\d.]+)', message, re.IGNORECASE)
    if sl_match:
        sl = sl_match.group(1) or sl_match.group(2)
        signal['sl'] = float(sl)

    # ✅ Target (at least TP1)
    tp_match = re.findall(r'(TP\d?|Target\d?)[:=]?\s*\$?([\d.]+)', message, re.IGNORECASE)
    if tp_match:
        tps = [float(tp[1]) for tp in tp_match[:2]]  # only up to TP2
        signal['tp'] = tps

    return signal
