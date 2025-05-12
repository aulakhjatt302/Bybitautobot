from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import asyncio
import os
from dotenv import load_dotenv
from signal_parser import parse_signal
from trade_manager import execute_trade
from indicators import check_indicators
from pybit.unified_trading import HTTP
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

bot_enabled = True

# Initialize clients
try:
    client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except FloodWaitError as e:
    print(f"⚠️ FloodWaitError: Wait for {e.seconds} seconds before bot login.")
    client = None

bybit_client = HTTP(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=False
)

# Dummy HTTP Server
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running (dummy server)!")

def run_dummy_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, DummyHandler)
    httpd.serve_forever()

# Bot Handlers
if client:
    CHANNELS = {
        '@Binance_pump_Crypto_Future': 'Group 1',
        '@binance_360': 'Group 2',
        '@cryptoleaopards': 'Group 3',
        '@crptobserver': 'Group 4',
    }

    for channel, name in CHANNELS.items():
        @client.on(events.NewMessage(chats=channel))
        async def signal_handler(event, channel_name=name):
            global bot_enabled
            if not bot_enabled:
                print(f"⚠️ Bot OFF. Ignoring message from {channel_name}")
                return
            try:
                print(f"📩 Message from {channel_name}:\n{event.message.text}")
                signal = parse_signal(event.message.text)
                print("🧠 Parsed signal:", signal)

                if check_indicators(signal['symbol']):
                    print("✅ Indicators OK. Executing trade...")
                    await execute_trade(signal)
                else:
                    print(f"⚠️ Indicators not favorable for {signal['symbol']}. Trade skipped.")

            except Exception as e:
                print(f"❌ Error during signal handling: {str(e)}")

    @client.on(events.NewMessage(from_users=OWNER_ID))
    async def command_handler(event):
        global bot_enabled
        cmd = event.message.text.lower().strip()

        if cmd == "/on":
            bot_enabled = True
            await event.respond("✅ Bot turned ON.")
        elif cmd == "/off":
            bot_enabled = False
            await event.respond("⛔ Bot turned OFF.")
        elif cmd == "/status":
            await event.respond(f"ℹ️ Bot is {'ON' if bot_enabled else 'OFF'}.")
        elif cmd == "/balance":
            try:
                balance_info = bybit_client.get_wallet_balance(accountType="UNIFIED")
                usdt_info = balance_info['result']['list'][0]['coin']
                for coin in usdt_info:
                    if coin['coin'] == "USDT":
                        available_balance = coin['availableToWithdraw']
                        break
                await event.respond(f"💰 Wallet Balance: {available_balance} USDT")
            except Exception as e:
                await event.respond(f"❌ Error fetching balance: {str(e)}")
        elif cmd == "/openpositions":
            try:
                positions = bybit_client.get_positions(category="linear")['result']['list']
                if positions:
                    msg = "🪙 Open Positions:\n"
                    for p in positions:
                        if float(p['size']) > 0:
                            side = p['side']
                            qty = p['size']
                            entry = p['avgEntryPrice']
                            symbol = p['symbol']
                            msg += f"- {symbol} {side}: {qty} Qty, Entry: {entry}\n"
                    await event.respond(msg)
                else:
                    await event.respond("📭 No Open Positions.")
            except Exception as e:
                await event.respond(f"❌ Error fetching open positions: {str(e)}")
        else:
            await event.respond("ℹ️ Available Commands:\n/on\n/off\n/status\n/balance\n/openpositions")

    async def debug_log():
        while True:
            print("👂 Bot is running... waiting for signals & commands...")
            await asyncio.sleep(30)

# Start Everything
if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()

    if client:
        with client:
            client.loop.create_task(debug_log())
            client.run_until_disconnected()
    else:
        print("❌ Bot cannot start due to FloodWaitError. Please wait and redeploy later.")
