import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def apply_indicators(df):
    # Ensure 'close' is float
    df['close'] = df['close'].astype(float)

    # EMA calculations
    df['ema_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    df['ema_200'] = EMAIndicator(close=df['close'], window=200).ema_indicator()

    # RSI calculation
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()

    return df

def get_signal(df):
    latest = df.iloc[-1]

    if latest['ema_50'] > latest['ema_200'] and latest['rsi'] < 30:
        return 'BUY'
    elif latest['ema_50'] < latest['ema_200'] and latest['rsi'] > 70:
        return 'SELL'
    else:
        return 'HOLD'
