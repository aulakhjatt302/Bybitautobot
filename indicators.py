import requests
import os

TAAPI_KEY = os.getenv("TAAPI_KEY")

def check_indicators(symbol):
    try:
        url = f"https://api.taapi.io/rsi?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval=5m"
        resp = requests.get(url).json()
        rsi = resp.get("value", 50)
        print(f"RSI = {rsi}")
        return rsi < 70
    except Exception as e:
        print("Indicator fallback:", e)
        return True
