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
OWNER_ID = int(os.getenv("OWNER_ID"))  # Your Telegram user ID

bot_enabled = True
client = TelegramClient("userbot", API_ID, API_HASH)

CHANNELS = {
    '@Binance_pump_Crypto_Future': 'Group 1',
    '@binance_360': 'Group 2',
    '@cryptoleaopards': 'Group 3',
    '@crptobserver': 'Group 4',
}

for channel, name in CHANNELS.items():
    @client.on(events.NewMessage(chats=channel))
    async def handler(event, channel_name=name):
        global bot_enabled
        if not bot_enabled:
            print("Bot is OFF. Ignoring signal.")
            return
        print(f"📩 Message from {channel_name} ({channel}):")
        print(event.message.text)
        signal = parse_signal(event.message.text)
        print("🧠 Parsed Signal:", signal)
        if check_indicators(signal['symbol']):
            print("✅ Indicators passed. Executing trade...")
            execute_trade(signal)
            await event.reply("✅ Trade executed based on signal!")
        else:
            print("❌ Indicators failed. No trade executed.")
            await event.reply("⚠️ Signal ignored due to market condition.")

@client.on(events.NewMessage(chats=lambda chat: chat.id == OWNER_ID))
async def control(event):
    global bot_enabled
    msg = event.message.text.lower()
    if msg == "/on":
        bot_enabled = True
        await event.respond("✅ Bot turned ON.")
    elif msg == "/off":
        bot_enabled = False
        await event.respond("⛔ Bot turned OFF.")
    elif msg == "/status":
        status = "ON" if bot_enabled else "OFF"
        await event.respond(f"ℹ️ Bot is currently: {status}")
    else:
        await event.respond("Use /on, /off, or /status.")

async def debug_log():
    while True:
        print("👂 Bot running... Listening for signals and commands...")
        await asyncio.sleep(30)

if __name__ == '__main__':
    with client:
        client.loop.create_task(debug_log())
        client.run_until_disconnected()
