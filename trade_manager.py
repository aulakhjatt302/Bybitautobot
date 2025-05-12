# trade_manager.py

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from pybit.unified_trading import HTTP
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# Initialize Bybit Client
bybit_client = HTTP(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=False
)

# Initialize Telegram Notify Client
notify = None
try:
    notify = TelegramClient("notify_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except FloodWaitError as e:
    print(f"⚠️ FloodWaitError: Wait for {e.seconds} seconds before Telegram Notify client will work.")
    notify = None

# Notify function
async def notify_owner(message):
    if notify:
        await notify.send_message(OWNER_ID, message)
    else:
        print("Notification skipped due to FloodWaitError.")

# Execute Trade Function with Safe OCO Logic
async def execute_trade(signal_data):
    try:
        symbol = signal_data.get("symbol", "BTCUSDT")
        side = signal_data.get("side", "LONG")
        entry_price = float(signal_data.get("entry", 0))
        sl_price = float(signal_data.get("sl", 0))
        tp_list = signal_data.get("tp", [])
        qty = 25 / entry_price  # Approx $25 per trade
        qty = round(qty, 4)  # round to 4 decimals for Bybit

        # Determine side for exit orders
        exit_side = "Sell" if side == "LONG" else "Buy"

        # Set leverage to 10x
        bybit_client.set_leverage(
            category="linear",
            symbol=symbol,
            buy_leverage=10,
            sell_leverage=10
        )

        # Place Market Entry
        entry_order = bybit_client.place_order(
            category="linear",
            symbol=symbol,
            side="Buy" if side == "LONG" else "Sell",
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False
        )

        print(f"✅ Entry Order Placed: {entry_order}")

        # After successful entry, place SL and TP
        if len(tp_list) > 0:
            tp_price = tp_list[0]  # Use first target for safe exit
        else:
            tp_price = entry_price * 1.01 if side == "LONG" else entry_price * 0.99  # fallback

        # Place Take Profit Order
        tp_order = bybit_client.place_order(
            category="linear",
            symbol=symbol,
            side=exit_side,
            order_type="Limit",
            qty=qty,
            price=str(round(tp_price, 4)),
            time_in_force="GoodTillCancel",
            reduce_only=True
        )

        # Place Stop Loss Order
        sl_order = bybit_client.place_order(
            category="linear",
            symbol=symbol,
            side=exit_side,
            order_type="Limit",
            qty=qty,
            price=str(round(sl_price, 4)),
            time_in_force="GoodTillCancel",
            reduce_only=True
        )

        print(f"✅ TP and SL Orders Placed.")

        # Notify owner
        msg = f"✅ Trade Live:\nSymbol: {symbol}\nSide: {side}\nEntry: {entry_price}\nTP: {tp_price}\nSL: {sl_price}\nQty: {qty}"
        asyncio.create_task(notify_owner(msg))

    except Exception as e:
        print(f"❌ Error placing trade: {e}")
        await notify_owner(f"❌ Error placing trade: {e}")
