import os
from pybit.unified_trading import HTTP
from telethon.sync import TelegramClient

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

notify = TelegramClient("notify_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

session = HTTP(
    testnet=False,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)

async def execute_trade(signal):
    try:
        symbol = signal['symbol']
        side = signal['side'].upper()
        qty = 25
        leverage = 10

        session.set_leverage(category="linear", symbol=symbol, buyLeverage=leverage, sellLeverage=leverage)

        order = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=qty,
            timeInForce="GoodTillCancel"
        )

        msg = f"✅ Trade Placed:\n{symbol} | {side}\nQty: {qty}, Leverage: {leverage}"
        await notify.send_message(OWNER_ID, msg)
        print("✅ Trade placed and user notified.")

    except Exception as e:
        error_msg = f"❌ Trade Failed: {e}"
        print(error_msg)
        await notify.send_message(OWNER_ID, error_msg)
