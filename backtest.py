from oanda_api import fetch_candles
from strategy import apply_indicators, get_signal

def backtest():
    df = fetch_candles(count=500)  # last 500 hours
    df = apply_indicators(df)
    
    signals = []
    for i in range(200, len(df)):  # skip until indicators are ready
        signal = get_signal(df.iloc[:i+1])
        signals.append(signal)

    df = df.iloc[200:]
    df["signal"] = signals

    print(df[["close", "ema_50", "ema_200", "rsi", "signal"]].tail(10))

if __name__ == "__main__":
    backtest()
