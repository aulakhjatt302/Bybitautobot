from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv
from telethon import TelegramClient
import asyncio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

notify = TelegramClient("notify_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

session = HTTP(
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET"),
    testnet=False,
)

async def execute_trade(signal):
    try:
        symbol = signal['symbol']
        side = signal['side']
        entry_price = signal['entry']
        sl = signal['sl']
        tps = signal.get('tp', [])

        # ✅ Default config
        qty = 25  # USDT worth
        leverage = 10

        # ✅ Set leverage
        session.set_leverage(category="linear", symbol=symbol, buy_leverage=leverage, sell_leverage=leverage)

        # ✅ Market order
        order = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False,
        )

        print(f"✅ Trade Placed: {symbol} | {side} | Qty: {qty}")
        await notify.send_message(OWNER_ID, f"✅ Trade Executed\n{symbol} | {side}\nEntry: {entry_price}\nSL: {sl}\nTP: {tps[:2]}")

    except Exception as e:
        print("❌ Trade Error:", e)
        await notify.send_message(OWNER_ID, f"❌ Trade Failed:\n{e}")
