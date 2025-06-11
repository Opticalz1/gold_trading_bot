import pandas as pd
import ta

# === EMA Strategy ===
def ema_signal(df):
    df = df.copy()
    df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=2).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=10).ema_indicator()
    df['ema_signal'] = None
    df.loc[df['ema_fast'] > df['ema_slow'], 'ema_signal'] = 'BUY'
    df.loc[df['ema_fast'] < df['ema_slow'], 'ema_signal'] = 'SELL'
    return df['ema_signal']

# === MACD Strategy ===
def macd_signal(df):
    df = df.copy()
    macd = ta.trend.MACD(df['close'], window_fast=5, window_slow=20, window_sign=5)
    df['macd_diff'] = macd.macd_diff()
    df['macd_signal'] = None
    df.loc[df['macd_diff'] > 0, 'macd_signal'] = 'BUY'
    df.loc[df['macd_diff'] < 0, 'macd_signal'] = 'SELL'
    return df['macd_signal']

# === OrderBlock Strategy ===
def orderblock_signal(df):
    df = df.copy()
    window = 5
    threshold = -0.5
    df['mean'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['z_score'] = (df['close'] - df['mean']) / df['std']
    df['ob_signal'] = None
    df.loc[df['z_score'] > threshold, 'ob_signal'] = 'BUY'
    df.loc[df['z_score'] < -threshold, 'ob_signal'] = 'SELL'
    return df['ob_signal']

# === Combined Strategy with Voting ===
def triple_confirm_strategy(m1_df, m3_df, m5_df):
    sig_ema = ema_signal(m1_df)
    sig_macd = macd_signal(m3_df)
    sig_ob   = orderblock_signal(m5_df)

    combined = pd.DataFrame(index=m1_df.index)
    combined['EMA'] = sig_ema
    combined['MACD'] = sig_macd.reindex(m1_df.index, method='ffill')
    combined['OB'] = sig_ob.reindex(m1_df.index, method='ffill')

    def vote(row):
        votes = [row['EMA'], row['MACD'], row['OB']]
        if votes.count('BUY') >= 2:
            return 'BUY'
        elif votes.count('SELL') >= 2:
            return 'SELL'
        else:
            return None

    combined['signal'] = combined.apply(vote, axis=1)
    return combined['signal']

strategies = {
    "TripleConfirm": {
        "func": triple_confirm_strategy
    }
}
"""
