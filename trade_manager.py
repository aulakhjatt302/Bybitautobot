import os
from pybit import usdt_perpetual

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

session = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com",
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)

def execute_trade(signal):
    symbol = signal['symbol']
    side = signal['side']
    qty = 25
    leverage = 10
    session.set_leverage(symbol=symbol, buy_leverage=leverage, sell_leverage=leverage)
    order = session.place_active_order(
        symbol=symbol,
        side=side,
        order_type="Market",
        qty=qty,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False
    )
    print("Order:", order)
