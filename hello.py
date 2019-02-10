import configparser
import json
from datetime import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from oandapyV20 import API
from oandapyV20.endpoints import accounts, instruments

def main():
    config = configparser.ConfigParser()
    config.read('oanda.cfg')

    ACCOUNT_ID = config['oanda']['account_id']
    API_TOKEN = config['oanda']['account_token']
    INSTRUMENTS = ["USD_CAD","EUR_USD","USD_CHF","GBP_USD","NZD_USD","AUD_USD","USD_JPY","EUR_CAD","EUR_AUD","EUR_JPY","EUR_CHF","EUR_GBP","AUD_CAD","GBP_CHF","GBP_JPY","CHF_JPY","AUD_JPY","AUD_NZD"]

    api = API(access_token=API_TOKEN)

    instrument_req = accounts.AccountInstruments(ACCOUNT_ID)
    instrument_res = api.request(instrument_req)

    all_instruments = [i['name'] for i in instrument_res['instruments']]
    
    candlestick_req = instruments.InstrumentsCandles(
        'EUR_CAD',
        params= {
            "from": '2019-02-05',
            "to": '2019-02-07',
            "granularity": "M1",
            "price": "A"
        }
    )
    candlestick_res = api.request(candlestick_req)
    candles = candlestick_res['candles']
    print(candles[1])
    for i in range(len(candles)):
        clean_data = {
            'time': candles[i]['time'],
            'volume': candles[i]['volume'],
            'complete': candles[i]['complete'],
            'open': candles[i]['ask']['o'],
            'close': candles[i]['ask']['c'],
            'high': candles[i]['ask']['h'],
            'low': candles[i]['ask']['l'],
        }
        candles[i] = clean_data

    df = pd.DataFrame(candles).set_index('time')
    df.index = pd.DatetimeIndex(df.index)
    df['open'] = df['open'].astype(float)
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df.info()


    # FIGURE OUT WTH IS HAPPENING HERE

    # df['returns'] = np.log(df['close'] / df['close'].shift(1))
    df['returns'] = np.log(df['close'] / df['open'])
    df.info()

    cols = []

    for momentum in [15, 30, 60, 120]:
        col = 'position_%s' % momentum
        df[col] = np.sign(df['returns'].rolling(momentum).mean())
        cols.append(col)
    

    strats = ['returns']

    for col in cols:
        strat = 'strategy_%s' % col.split('_')[1]
        df[strat] = df[col].shift(1) * df['returns']
        strats.append(strat)
    
    # plots the percent change from starting point
    plot = df[strats].dropna().cumsum().apply(np.exp).plot()
    plt.show(plot)

if __name__ == "__main__":
    main()