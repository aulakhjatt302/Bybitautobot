import os
from pybit.unified_trading import HTTP

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

session = HTTP(
    testnet=False,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)

def execute_trade(signal):
    symbol = signal['symbol']
    side = signal['side'].upper()
    qty = 25
    leverage = 10

    # Set leverage
    session.set_leverage(category="linear", symbol=symbol, buyLeverage=leverage, sellLeverage=leverage)

    # Place order
    order = session.place_order(
        category="linear",
        symbol=symbol,
        side=side,
        orderType="Market",
        qty=qty,
        timeInForce="GoodTillCancel"
    )

    print("Order response:", order)
