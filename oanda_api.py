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
        balance = float(response['account']['balance'])
        return balance
    except Exception as e:
        print("Error getting account balance:", e)
        return 0

def place_trade(instrument, signal, risk_percent=2, stop_loss_pips=50):
    try:
        balance = get_account_balance()
        if balance == 0:
            print("⚠️ Unable to retrieve account balance.")
            return

        # Calculate max risk in currency
        max_risk_amount = balance * (risk_percent / 100)

        # Estimate pip value for 1 unit (simplified for major pairs and gold)
        pip_value_per_unit = 0.1 if "XAU" in instrument else 0.0001

        # Units = max risk / (pip value * stop loss)
        units = int(max_risk_amount / (pip_value_per_unit * stop_loss_pips))
        if signal == "SELL":
            units = -units

        order_data = {
            "order": {
                "instrument": instrument,
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {
                    "distance": str(stop_loss_pips * pip_value_per_unit)
                }
            }
        }

        r = orders.OrderCreate(accountID=OANDA_ACCOUNT_ID, data=order_data)
        response = client.request(r)
        print(f"✅ TRADE EXECUTED on {instrument}: {signal} | Units: {units}")
        print(response)

    except V20Error as e:
        print(f"❌ OANDA ERROR on {instrument}: {e}")
