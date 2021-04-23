import pandas as pd


def iterate_days(df):
    df.index = pd.to_datetime(df.time)
    df['date'] = df.index.date
    groups = df.groupby('date')
    for date, df in groups:
        yield date, df
