# trade_manager.py

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from pybit.unified_trading import HTTP
import os
import asyncio

# Env Variables
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
    print(f"⚠️ FloodWaitError: Wait for {e.seconds} seconds before Telegram client will work.")
    notify = None

# Function to notify owner on Telegram
async def notify_owner(message):
    if notify:
        await notify.send_message(OWNER_ID, message)
    else:
        print("Notification skipped due to FloodWaitError.")

# Function to Execute Trade
def execute_trade(signal_data):
    try:
        # Example trade data
        side = signal_data.get("side", "Buy")    # Buy or Sell
        symbol = signal_data.get("symbol", "BTCUSDT")
        qty = float(signal_data.get("qty", 0.001))
        leverage = int(signal_data.get("leverage", 10))

        # Set leverage
        bybit_client.set_leverage(
            category="linear",
            symbol=symbol,
            buy_leverage=leverage,
            sell_leverage=leverage,
        )

        # Place order
        order = bybit_client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel"
        )

        print(f"✅ Order Placed: {order}")

        # Notify on Telegram
        msg = f"Trade executed:\nSymbol: {symbol}\nSide: {side}\nQty: {qty}\nLeverage: {leverage}"
        asyncio.create_task(notify_owner(msg))

    except Exception as e:
        print(f"❌ Error placing trade: {e}")
