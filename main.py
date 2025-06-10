print("🚀 Starting multi-market trading bot with Bollinger Band Squeeze strategy...")

from oanda_api import fetch_candles
from strategy import bollinger_squeeze_signal
from notifier import send_telegram

import oandapyV20
import oandapyV20.endpoints.orders as orders
from dotenv import load_dotenv
import os
import schedule
import time

# Load credentials
load_dotenv("config.env")
API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")

client = oandapyV20.API(access_token=API_KEY)

# Settings
symbols = ["XAU_USD", "EUR_USD", "GBP_USD"]
account_balance = 100000
risk_percent = 0.02
sl_distance = 2.0
tp_distance = 4.0

def place_trade(symbol, signal_direction, current_price):
    risk_amount = account_balance * risk_percent
    units = int(risk_amount / sl_distance)

    if signal_direction == "SELL":
        units = -units

    # Calculate SL and TP levels
    if units > 0:
        stop_loss_price = round(current_price - sl_distance, 3)
        take_profit_price = round(current_price + tp_distance, 3)
    else:
        stop_loss_price = round(current_price + sl_distance, 3)
        take_profit_price = round(current_price - tp_distance, 3)

    order = {
        "order": {
            "instrument": symbol,
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "takeProfitOnFill": {"price": str(take_profit_price)},
            "stopLossOnFill": {"price": str(stop_loss_price)}
        }
    }

    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
    client.request(r)
    print(f"✅ Trade executed for {symbol}:", r.response)

    send_telegram(
        f"🚨 {signal_direction} {symbol}\n"
        f"Size: {abs(units)} units\n"
        f"Entry: {current_price}\n"
        f"SL: {stop_loss_price} | TP: {take_profit_price}"
    )

    with open("trades.csv", "a") as file:
        file.write(f"{time.ctime()},{symbol},{signal_direction},{current_price},{stop_loss_price},{take_profit_price},{units}\n")

def run_bot():
    for symbol in symbols:
        print(f"\n🧠 Running strategy for {symbol}...")
        df = fetch_candles(symbol=symbol, count=300, granularity="M30")
        signal = bollinger_squeeze_signal(df)

        print(f"📢 {symbol} Signal:", signal)

        if signal in ["BUY", "SELL"]:
            current_price = df['close'].iloc[-1]
            place_trade(symbol, signal, current_price)
        else:
            print(f"🟡 No trade signal for {symbol}.")

schedule.every(30).minutes.do(run_bot)

print("📅 Bot is running... Press CTRL+C to stop.")
run_bot()

while True:
    schedule.run_pending()
    time.sleep(1)
