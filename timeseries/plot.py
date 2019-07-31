import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import timeseries_config as cfg


def main():
    df = pd.read_csv(cfg.csv_file)
    df['year'] = pd.DatetimeIndex(df['timestamp']).year
    df = df[(df['year'] >= cfg.start_date) & (df['year'] <= cfg.end_date)]

    for feature in cfg.features:
        plt.figure(figsize=cfg.plot_size)
        sns.set_palette(cfg.plot_palette)
        sns.lineplot(x='year', y=feature, data=df)
        plt.savefig('output/' + feature + '.' + cfg.plot_format, format=cfg.plot_format)

    return


main()
