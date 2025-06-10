import pandas as pd
import numpy as np

def bollinger_squeeze_signal(df, window=20, num_std=2):
    df = df.copy()

    # Calculate Bollinger Bands
    df['ma'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['upper'] = df['ma'] + num_std * df['std']
    df['lower'] = df['ma'] - num_std * df['std']
    df['bandwidth'] = df['upper'] - df['lower']

    # Calculate squeeze (normalized bandwidth)
    df['squeeze'] = df['bandwidth'] / df['ma']

    # Check last values
    if len(df) < window + 5:
        return None

    recent = df.iloc[-5:]
    last = df.iloc[-1]

    # Entry signal logic
    if recent['squeeze'].min() < 0.01:  # low squeeze
        if last['close'] > last['upper']:
            return "BUY"
        elif last['close'] < last['lower']:
            return "SELL"

    return None
