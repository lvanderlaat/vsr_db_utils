import pandas as pd


def iterate_days(cat_filepath):
    df = pd.read_csv(cat_filepath)
    df.index = pd.to_datetime(df.time)
    df['date'] = df.index.date
    groups = df.groupby('date')
    for date, df in groups:
        yield date, df
