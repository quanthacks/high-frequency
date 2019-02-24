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
    fig, ax = plt.subplots()
    candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6)
    ax.xaxis.set_major_locator
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))

    # def mydate(x,pos):
    #     try:
    #         return xdate[int(x)]
    #     except IndexError:
    #         return ''

    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))

    # fig.autofmt_xdate()
    fig.tight_layout()

    # plt.show()


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
    # plt.show(plot)

    class MomentumTrader(pricing.PricingStream):  # 25
        def __init__(self, momentum, account_id, *args, **kwargs):  # 26
            print(kwargs)
            pricing.PricingStream.__init__(self, account_id, kwargs)  # 27
            self.ticks = 0  # 28
            self.position = 0  # 29
            self.df = pd.DataFrame()  # 30
            self.momentum = momentum  # 31
            self.units = 100000  # 32
        def create_order(self, side, units):  # 33
            order_data = {
                'units': units,
                'side': side,
                'type': 'market',
            }
            order = orders.OrderCreate(config['oanda']['account_id'], json.dumps(order_data))  # 34
            print('\n', order)  # 35
        def on_success(self, data):  # 36
            self.ticks += 1  # 37
            # print(self.ticks, end=', ')
            # appends the new tick data to the DataFrame object
            self.df = self.df.append(pd.DataFrame(data['tick'],
                                    index=[data['tick']['time']]))  # 38
            # transforms the time information to a DatetimeIndex object
            self.df.index = pd.DatetimeIndex(self.df['time'])  # 39
            # resamples the data set to a new, homogeneous interval
            dfr = self.df.resample('5s').last()  # 40
            # calculates the log returns
            dfr['returns'] = np.log(dfr['ask'] / dfr['ask'].shift(1))  # 41
            # derives the positioning according to the momentum strategy
            dfr['position'] = np.sign(dfr['returns'].rolling( 
                                        self.momentum).mean())  # 42
            if dfr['position'].ix[-1] == 1:  # 43
                # go long
                if self.position == 0:  # 44
                    self.create_order('buy', self.units)  # 45
                elif self.position == -1:  # 46
                    self.create_order('buy', self.units * 2)  # 47
                self.position = 1  # 48
            elif dfr['position'].ix[-1] == -1:  # 49
                # go short
                if self.position == 0:  # 50
                    self.create_order('sell', self.units)  # 51
                elif self.position == 1: # 52
                    self.create_order('sell', self.units * 2)  # 53
                self.position = -1  # 54
            if self.ticks == 250:  # 55
                # close out the position
                if self.position == 1:  # 56
                    self.create_order('sell', self.units)  # 57
                elif self.position == -1:  # 58
                    self.create_order('buy', self.units)  # 59
                self.disconnect()  # 60

    mt = MomentumTrader(momentum=12,
                        account_id=config['oanda']['account_id'],
                        environment='practice')

if __name__ == "__main__":
    main()