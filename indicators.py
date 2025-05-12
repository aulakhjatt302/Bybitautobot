import requests
import os
from dotenv import load_dotenv

load_dotenv()
TAAPI_SECRET = os.getenv("TAAPI_SECRET")

def check_indicators(symbol):
    pair = symbol.replace("USDT", "/USDT")
    url = f"https://api.taapi.io/rsi?secret={TAAPI_SECRET}&exchange=binance&symbol={pair}&interval=5m"
    
    try:
        r = requests.get(url)
        rsi = r.json().get("value", 50)
        print(f"📊 RSI = {rsi}")
        return rsi < 70 if "LONG" in symbol else rsi > 30
    except Exception as e:
        print(f"❌ TAAPI error: {e}")
        return False
