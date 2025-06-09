print("🚀 Starting multi-market trading bot...")

from oanda_api import fetch_candles
from strategy import apply_indicators, get_signal
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

# Instruments to trade
instruments = ["XAU_USD", "EUR_USD", "GBP_USD"]

def place_trade(instrument, signal_direction):
    # Fetch current price
    df = fetch_candles(instrument=instrument, count=2, granularity="M30")
    current_price = df['close'].iloc[-1]

    # Risk management
    account_balance = 100000  # Simulated
    risk_percent = 0.02
    sl_distance = 2.0
    tp_distance = 4.0
    risk_amount = account_balance * risk_percent
    units = int(risk_amount / sl_distance)

    if signal_direction == "SELL":
        units = -units

    if units > 0:
        stop_loss_price = round(current_price - sl_distance, 3)
        take_profit_price = round(current_price + tp_distance, 3)
    else:
        stop_loss_price = round(current_price + sl_distance, 3)
        take_profit_price = round(current_price - tp_distance, 3)

    order = {
        "order": {
            "instrument": instrument,
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "takeProfitOnFill": {"price": str(take_profit_price)},
            "stopLossOnFill": {"price": str(stop_loss_price)}
        }
    }

    try:
        r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
        client.request(r)
        print(f"✅ Trade executed for {instrument}:", r.response)

        # Telegram alert
        direction = "BUY" if units > 0 else "SELL"
        send_telegram(
            f"🚨 {direction} {instrument}
"
            f"Size: {abs(units)} units
"
            f"Entry: {current_price}
"
            f"SL: {stop_loss_price} | TP: {take_profit_price}"
        )

        # Log to CSV
        with open("trades.csv", "a") as file:
            file.write(f"{time.ctime()},{instrument},{direction},{current_price},{stop_loss_price},{take_profit_price},{units}\n")
    except Exception as e:
        print(f"❌ Error placing trade for {instrument}: {e}")

def run_bot():
    print("\n🧠 Running strategy...")
    for instrument in instruments:
        try:
            df = fetch_candles(instrument=instrument, count=300, granularity="M30")
            df = apply_indicators(df)
            signal = get_signal(df)
            print(f"📢 {instrument} Signal:", signal)
            if signal in ["BUY", "SELL"]:
                place_trade(instrument, signal)
            else:
                print(f"🟡 No trade signal for {instrument}.")
        except Exception as e:
            print(f"⚠️ Failed to process {instrument}: {e}")

# Schedule every 30 minutes
schedule.every(30).minutes.do(run_bot)

print("📅 Bot is running... Press CTRL+C to stop.")
run_bot()

while True:
    schedule.run_pending()
    time.sleep(1)
