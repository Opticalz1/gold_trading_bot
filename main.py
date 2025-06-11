# Rewriting the uploaded main.py file to use the triple-confirmation strategy with M1/M3/M5 logic

main_tripleconfirm = """
print("🚀 Starting multi-market trading bot with Triple Confirmation strategy...")

from oanda_api import fetch_candles
from strategy import strategies
from notifier import send_telegram

import oandapyV20
import oandapyV20.endpoints.orders as orders
from dotenv import load_dotenv
import os
import schedule
import time
import pandas as pd

# Load credentials
load_dotenv("config.env")
API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")

client = oandapyV20.API(access_token=API_KEY)

# Settings
symbols = ["XAU_USD", "EUR_USD", "GBP_USD"]
sl_distance = 2.0
tp_distance = 4.0
units = 50
strategy_func = strategies["TripleConfirm"]["func"]
last_signal = {}

def place_trade(symbol, signal_direction, current_price):
    trade_units = units if signal_direction == "BUY" else -units

    # SL and TP
    if trade_units > 0:
        stop_loss_price = round(current_price - sl_distance, 3)
        take_profit_price = round(current_price + tp_distance, 3)
    else:
        stop_loss_price = round(current_price + sl_distance, 3)
        take_profit_price = round(current_price - tp_distance, 3)

    order = {
        "order": {
            "instrument": symbol,
            "units": str(trade_units),
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
    f"⚡️ TRADE EXECUTED ⚡️\\n"
    f"📊 Symbol: {symbol}\\n"
    f"🎯 Direction: {signal_direction}\\n"
    f"💰 Entry: {current_price}\\n"
    f"🛡 SL: {stop_loss_price} | 🎯 TP: {take_profit_price}"
)

    with open("trades.csv", "a") as file:
        file.write(f"{time.ctime()},{symbol},{signal_direction},{current_price},{stop_loss_price},{take_profit_price},{units}\\n")

def run_bot():
    for symbol in symbols:
        print(f"\\n🧠 Running TripleConfirm for {symbol}...")

        try:
            df_m1 = fetch_candles(symbol=symbol, granularity="M1", count=200)
            df_m3 = fetch_candles(symbol=symbol, granularity="M3", count=200)
            df_m5 = fetch_candles(symbol=symbol, granularity="M5", count=200)

            signal_series = strategy_func(df_m1, df_m3, df_m5)
            signal = signal_series.dropna().iloc[-1] if not signal_series.dropna().empty else None

            print(f"📢 {symbol} Signal:", signal)

            if signal in ["BUY", "SELL"] and last_signal.get(symbol) != signal:
                current_price = df_m1['close'].iloc[-1]
                place_trade(symbol, signal, current_price)
                last_signal[symbol] = signal
            else:
                print(f"🟡 No new signal for {symbol}.")

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

schedule.every(1).minutes.do(run_bot)

print("📅 Bot is running... Press CTRL+C to stop.")
run_bot()

while True:
    schedule.run_pending()
    time.sleep(1)
"""

# Save updated main.py
path = "/mnt/data/main.py"
with open(path, "w") as f:
    f.write(main_tripleconfirm)

path

