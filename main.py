from telethon import TelegramClient, events
import asyncio
import os
from dotenv import load_dotenv
from signal_parser import parse_signal
from trade_manager import execute_trade
from indicators import check_indicators

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot_enabled = True

# Create bot client with token
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Telegram channels to listen
CHANNELS = {
    '@Binance_pump_Crypto_Future': 'Group 1',
    '@binance_360': 'Group 2',
    '@cryptoleaopards': 'Group 3',
    '@crptobserver': 'Group 4',
}

# Listen to each channel separately
for channel, name in CHANNELS.items():
    @client.on(events.NewMessage(chats=channel))
    async def handler(event, channel_name=name):
        global bot_enabled
        if not bot_enabled:
            print("⚠️ Bot is OFF. Ignoring signal.")
            return
        print(f"📩 Message from {channel_name} ({channel}):\n{event.message.text}")

        signal = parse_signal(event.message.text)
        print("🧠 Parsed Signal:", signal)

        if check_indicators(signal['symbol']):
            print("✅ Indicators passed. Executing trade...")
            execute_trade(signal)
            await event.reply("✅ Trade executed based on signal!")
        else:
            print("❌ Indicators failed. Signal skipped.")
            await event.reply("⚠️ Market condition not favorable. Trade skipped.")

# Telegram control commands: /on /off /status
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
        status = "ON" if bot_enabled else "OFF"
        await event.respond(f"ℹ️ Bot is currently: {status}")
    else:
        await event.respond("Use /on, /off, or /status")

# Background log every 30 sec
async def debug_log():
    while True:
        print("👂 Bot is running... Waiting for signals and commands...")
        await asyncio.sleep(30)

# Start the bot
if __name__ == '__main__':
    with client:
        client.loop.create_task(debug_log())
        client.run_until_disconnected()
