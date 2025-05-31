import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv("config.env")

API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")

client = oandapyV20.API(access_token=API_KEY)

def fetch_candles(instrument="XAU_USD", count=500, granularity="H1"):
    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"  # mid
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    client.request(r)
    candles = r.response['candles']

    data = []
    for c in candles:
        data.append({
            "time": c["time"],
            "open": float(c["mid"]["o"]),
            "high": float(c["mid"]["h"]),
            "low": float(c["mid"]["l"]),
            "close": float(c["mid"]["c"]),
            "volume": c["volume"]
        })

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    return df
