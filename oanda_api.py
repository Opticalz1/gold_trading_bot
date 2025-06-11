# Rewrite oanda_api.py completely to include account info, trade execution, and fetch_candles

oanda_api_complete = """
import os
import pandas as pd
from dotenv import load_dotenv
import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments

# Load API credentials
load_dotenv("config.env")
API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")

# Initialize OANDA API client
client = oandapyV20.API(access_token=API_KEY)

def get_account_balance():
    r = accounts.AccountDetails(accountID=ACCOUNT_ID)
    response = client.request(r)
    balance = float(response['account']['balance'])
    print(f"💰 Account Balance: {balance}")
    return balance

def place_trade(symbol, direction, units, sl_price=None, tp_price=None):
    trade_units = int(units) if direction == "BUY" else -int(units)

    order_data = {
        "order": {
            "instrument": symbol,
            "units": str(trade_units),
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }

    if sl_price and tp_price:
        order_data["order"]["stopLossOnFill"] = {"price": str(sl_price)}
        order_data["order"]["takeProfitOnFill"] = {"price": str(tp_price)}

    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order_data)

    try:
        client.request(r)
        print(f"✅ {direction} order placed for {symbol}")
        return r.response
    except Exception as e:
        print(f"❌ Failed to place order: {e}")
        return None

def fetch_candles(symbol, granularity="M1", count=200):
    try:
        params = {
            "granularity": granularity,
            "count": count,
            "price": "M"
        }

        r = instruments.InstrumentsCandles(instrument=symbol, params=params)
        response = client.request(r)

        data = []
        for candle in response["candles"]:
            data.append({
                "time": candle["time"],
                "open": float(candle["mid"]["o"]),
                "high": float(candle["mid"]["h"]),
                "low": float(candle["mid"]["l"]),
                "close": float(candle["mid"]["c"]),
                "volume": int(candle["volume"])
            })

        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        return df

    except Exception as e:
        print(f"❌ Failed to fetch candles for {symbol} ({granularity}): {e}")
        return pd.DataFrame()
"""

# Save to oanda_api.py
path = "/mnt/data/oanda_api.py"
with open(path, "w") as f:
    f.write(oanda_api_complete)

path
