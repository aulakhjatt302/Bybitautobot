from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import asyncio, os, sys, time
from dotenv import load_dotenv
from signal_parser import parse_signal
from trade_manager import execute_trade
from indicators import check_indicators
from pybit.unified_trading import HTTP
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TAAPI_SECRET = os.getenv("TAAPI_SECRET")

bot_enabled = True
last_activity_time = time.time()

try:
    client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except FloodWaitError as e:
    print(f"FloodWaitError: Wait {e.seconds} seconds")
    client = None

bybit_client = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=False)

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running (dummy server)!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 10000))
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DummyHandler)
    print(f"✅ Dummy HTTP Server running on port {PORT}")
    httpd.serve_forever()

def restart_program():
    print("Restarting bot after 3 minutes of inactivity...")
    os.execv(sys.executable, ['python'] + sys.argv)

async def auto_restart_checker():
    global last_activity_time
    while True:
        await asyncio.sleep(30)
        if time.time() - last_activity_time > 180:
            restart_program()

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
            global bot_enabled, last_activity_time
            if not bot_enabled:
                return
            try:
                last_activity_time = time.time()
                print(f"Signal from {channel_name}:\n{event.text}")
                signal = parse_signal(event.text)
                if check_indicators(signal['symbol']):
                    await execute_trade(signal)
            except Exception as e:
                print(f"Error in signal_handler: {e}")

    @client.on(events.NewMessage(from_users=OWNER_ID))
    async def command_handler(event):
        global bot_enabled, last_activity_time
        cmd = event.text.lower().strip()
        last_activity_time = time.time()

        try:
            if cmd == "/on":
                bot_enabled = True
                await event.respond("✅ Bot ON")
            elif cmd == "/off":
                bot_enabled = False
                await event.respond("⛔ Bot OFF")
            elif cmd == "/status":
                await event.respond(f"Bot is {'ON' if bot_enabled else 'OFF'}")
            elif cmd == "/balance":
                await event.respond("❌ Balance not available due to Bybit IP restriction.")
            elif cmd == "/openpositions":
                await event.respond("❌ Open Positions not supported on current IP.")
            else:
                await event.respond("/on /off /status")
        except Exception as e:
            await event.respond(f"❌ Error: {e}")

    async def heartbeat():
        while True:
            print("Bot running... waiting for signals...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    if client:
        with client:
            client.loop.create_task(auto_restart_checker())
            client.loop.create_task(heartbeat())
            client.run_until_disconnected()
