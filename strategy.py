import pandas as pd

def apply_indicators(df):
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()

    df['STD20'] = df['close'].rolling(window=20).std()
    df['UpperBB'] = df['EMA20'] + (2 * df['STD20'])
    df['LowerBB'] = df['EMA20'] - (2 * df['STD20'])

    df['BB_Width'] = df['UpperBB'] - df['LowerBB']
    df['BB_Squeeze'] = df['BB_Width'] < df['BB_Width'].rolling(window=20).mean()

    return df

def get_signal(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if prev['BB_Squeeze'] and not latest['BB_Squeeze']:
        if latest['close'] > latest['UpperBB'] and latest['EMA20'] > latest['EMA50']:
            return "BUY"
        elif latest['close'] < latest['LowerBB'] and latest['EMA20'] < latest['EMA50']:
            return "SELL"
    return "HOLD"
