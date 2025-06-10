from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
from oandapyV20.exceptions import V20Error
from config import OANDA_API_KEY, OANDA_ACCOUNT_ID

client = API(access_token=OANDA_API_KEY)

def get_account_balance():
    try:
        r = accounts.AccountDetails(accountID=OANDA_ACCOUNT_ID)
        response = client.request(r)
        return float(response['account']['balance'])
    except Exception as e:
        print("Error getting account balance:", e)
        return 0

def place_trade(instrument, signal):
    try:
        units = 100 if signal == "BUY" else -100

        order_data = {
            "order": {
                "instrument": instrument,
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }

        r = orders.OrderCreate(accountID=OANDA_ACCOUNT_ID, data=order_data)
        response = client.request(r)
        print(f"✅ TRADE EXECUTED on {instrument}: {signal} | Units: {units}")
        print(response)

    except V20Error as e:
        print(f"❌ OANDA ERROR on {instrument}: {e}")

