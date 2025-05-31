print("🚀 Starting gold trading bot...")

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

def place_trade(signal_direction):
    # Fetch current price
    df = fetch_candles(count=2, granularity="M30")
    current_price = df['close'].iloc[-1]

    # Risk management settings
    account_balance = 100000  # Simulated for paper account
    risk_percent = 0.02       # 2% risk per trade
    sl_distance = 2.0         # in USD
    tp_distance = 4.0         # in USD
    risk_amount = account_balance * risk_percent
    units = int(risk_amount / sl_distance)

    if signal_direction == "SELL":
        units = -units

    # Calculate SL and TP levels
    if units > 0:  # BUY
        stop_loss_price = round(current_price - sl_distance, 3)
        take_profit_price = round(current_price + tp_distance, 3)
    else:  # SELL
        stop_loss_price = round(current_price + sl_distance, 3)
        take_profit_price = round(current_price - tp_distance, 3)

    # Build order with SL/TP
    order = {
        "order": {
            "instrument": "XAU_USD",
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "takeProfitOnFill": {"price": str(take_profit_price)},
            "stopLossOnFill": {"price": str(stop_loss_price)}
        }
    }

    # Send to OANDA
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
    client.request(r)
    print("✅ Trade executed:", r.response)

    # Telegram alert
    direction = "BUY" if units > 0 else "SELL"
    send_telegram(
        f"🚨 {direction} XAU/USD\n"
        f"Size: {abs(units)} units\n"
        f"Entry: {current_price}\n"
        f"SL: {stop_loss_price} | TP: {take_profit_price}"
    )

    # Log to CSV
    with open("trades.csv", "a") as file:
        file.write(f"{time.ctime()},{direction},{current_price},{stop_loss_price},{take_profit_price},{units}\n")

def run_bot():
    print("\n🧠 Running strategy...")
    df = fetch_candles(count=300, granularity="M30")
    df = apply_indicators(df)
    signal = get_signal(df)

    print("📢 Signal:", signal)

    if signal in ["BUY", "SELL"]:
        place_trade(signal)
    else:
        print("🟡 No trade signal.")

# Schedule every 30 minutes
schedule.every(30).minutes.do(run_bot)

print("📅 Bot is running... Press CTRL+C to stop.")
run_bot()  # Run immediately

while True:
    schedule.run_pending()
    time.sleep(1)
