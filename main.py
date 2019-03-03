import configparser
import json
from datetime import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_finance import candlestick2_ohlc
from oandapyV20 import API
from oandapyV20.endpoints import accounts, instruments, orders, pricing
from data_manager import DataManager

def main():
    config = configparser.ConfigParser()
    config.read('oanda.cfg')

    ACCOUNT_ID = config['oanda']['account_id']
    API_TOKEN = config['oanda']['account_token']

    api = API(access_token=API_TOKEN)

    dm = DataManager(api, granularity="H1", td_days=2, instruments=['USD_CAD', 'EUR_USD'])
    print(dm.data)
    # df['returns'] = np.log(df['close'] / df['close'].shift(1))
    # df['returns'] = np.log(df['close'] / df['open'])
    # df.info()

    # cols = []

    # for momentum in [15, 30, 60, 120]:
    #     col = 'position_%s' % momentum
    #     df[col] = np.sign(df['returns'].rolling(momentum).mean())
    #     cols.append(col)

    # strats = ['returns']

    # for col in cols:
    #     strat = 'strategy_%s' % col.split('_')[1]
    #     df[strat] = df[col].shift(1) * df['returns']
    #     strats.append(strat)
    
    # plot = df[strats].dropna().cumsum().apply(np.exp).plot()
    # plt.show(plot)

if __name__ == "__main__":
    main()