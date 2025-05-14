from telethon import TelegramClient, events
import asyncio
import os
from dotenv import load_dotenv
from signal_parser import parse_signal
from trade_manager import execute_trade
from indicators import check_indicators

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot_enabled = True

# Start the Telegram client using bot token
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ✅ All Telegram channels/groups to monitor
CHANNELS = {
    '@Binance_pump_Crypto_Future': 'Group 1',
    '@binance_360': 'Group 2',
    '@cryptoleaopards': 'Group 3',
    '@crptobserver': 'Group 4',
    # -1001234567890: 'Test Group',  # ✅ यहाँ अपनी test group की सही ID डालें
}

# ✅ DEBUG Logger — prints every message + chat ID
@client.on(events.NewMessage())
async def debug_logger(event):
    try:
        print("📨 Message received!")
        print("📍 Chat ID:", event.chat_id)
        print("✉️ Message Text:", event.message.text)
    except Exception as e:
        print("❌ Error in debug_logger:", e)

# ✅ Signal handler for each group
for channel, name in CHANNELS.items():
    @client.on(events.NewMessage(chats=channel))
    async def signal_handler(event, channel_name=name):
        global bot_enabled
        if not bot_enabled:
            print(f"⛔ Bot is OFF. Skipping message from {channel_name}")
            return

        print(f"📩 Message from {channel_name}:")
        print(event.message.text)

        signal = parse_signal(event.message.text)
        print("🧠 Parsed Signal:", signal)

        if check_indicators(signal['symbol']):
            print("✅ Indicators OK. Executing trade...")
            await execute_trade(signal)
        else:
            msg = f"⚠️ Indicators not favorable for {signal['symbol']}. Trade skipped."
            await client.send_message(OWNER_ID, msg)
            print(msg)

# ✅ Telegram commands: /on /off /status
@client.on(events.NewMessage(from_users=OWNER_ID))
async def command_handler(event):
    global bot_enabled
    cmd = event.message.text.lower().strip()
    if cmd == "/on":
        bot_enabled = True
        await event.respond("✅ Bot is ON")
    elif cmd == "/off":
        bot_enabled = False
        await event.respond("⛔ Bot is OFF")
    elif cmd == "/status":
        await event.respond(f"ℹ️ Bot is {'ON' if bot_enabled else 'OFF'}")
    else:
        await event.respond("Use: /on /off /status")

# ✅ Dummy HTTP Server for Render (to bind port)
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running (Render OK)")

def run_dummy_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, DummyHandler)
    httpd.serve_forever()

# ✅ Debug ping every 30 sec
async def debug_log():
    while True:
        print("👂 Bot is running and listening...")
        await asyncio.sleep(30)

# ✅ Main Execution
if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    with client:
        client.loop.create_task(debug_log())
        client.run_until_disconnected()
