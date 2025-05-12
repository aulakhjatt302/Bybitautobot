import asyncio
from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
client = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=False)

async def execute_trade(signal):
    symbol = signal["symbol"]
    side = signal["side"]
    entry = signal["entry"]
    sl = signal["stop_loss"]
    tps = signal["targets"]

    qty = 20 / entry  # 20 USDT position sizing (adjust if needed)

    try:
        # Close any existing position
        client.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "LONG" else "Buy",
            orderType="Market",
            qty=qty,
            reduceOnly=True
        )
    except:
        pass  # no open position to close

    try:
        client.place_order(
            category="linear",
            symbol=symbol,
            side=side.title(),
            orderType="Limit",
            price=round(entry, 6),
            qty=qty,
            timeInForce="PostOnly",
            takeProfit=round(tps[1], 6) if len(tps) > 1 else None,
            stopLoss=round(sl, 6) if sl else None
        )
        print(f"✅ Order placed: {side} {symbol} at {entry}")
    except Exception as e:
        print(f"❌ Order error: {e}")
