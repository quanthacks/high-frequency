from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import numpy as np
from oandapyV20 import API
from oandapyV20.endpoints import accounts, instruments, orders, pricing

class DataManager:
    # td_days is timedelta in days. This represents the amount of historical data in days for each instrument
    # granularity is the Oanda candlestick granularity http://developer.oanda.com/rest-live-v20/instrument-ep/
    # instruments is a list of all instruments to gather data about
    def __init__(self,
                 api,
                 td_days=15,
                 granularity="M1",
                 instruments=["USD_CAD","EUR_USD","USD_CHF","GBP_USD","NZD_USD","AUD_USD","USD_JPY","EUR_CAD","EUR_AUD","EUR_JPY","EUR_CHF","EUR_GBP","AUD_CAD","GBP_CHF","GBP_JPY","CHF_JPY","AUD_JPY","AUD_NZD"],

    ):
        self.api = api
        self.td_days = td_days
        self.granularity = granularity
        self.instruments = instruments
        self.data = {}
        self.__init_instrument_data()

    def __data_points_per_hour(self):
        granularity_map = {
            "M": 60,
            "H": 1,
            "S": 3600
        }
        return granularity_map[self.granularity[0]] / int(self.granularity[1])

    def __init_instrument_data(self):
        # calculate the target number of candles so we don't have to deal with weekday conversion
        target_num_candles = self.td_days * (24 * self.__data_points_per_hour() - 1)
        curr_time = datetime.now(tz=timezone('US/Eastern'))
        response_data = {}
        for instrument in self.instruments:
            response_data[instrument] = []

        while True:
            to_date = curr_time.strftime("%Y-%m-%d")
            curr_time -= timedelta(days=1)
            from_date = curr_time.strftime("%Y-%m-%d")
            for instrument in self.instruments:
                candlestick_req = instruments.InstrumentsCandles(
                    instrument,
                    params= {
                        "from": from_date,
                        "to": to_date,
                        "granularity": self.granularity,
                        "price": "M"
                    }
                )
                candlestick_res = self.api.request(candlestick_req)
                candles = candlestick_res['candles']
                for i in range(len(candles) - 1, -1, -1):
                    clean_data = {
                        'time': candles[i]['time'],
                        'volume': candles[i]['volume'],
                        'complete': candles[i]['complete'],
                        'open': candles[i]['mid']['o'],
                        'close': candles[i]['mid']['c'],
                        'high': candles[i]['mid']['h'],
                        'low': candles[i]['mid']['l'],
                    }
                    response_data[instrument].insert(0, clean_data)
            if len(response_data[self.instruments[0]]) >= target_num_candles:
                break
        
        for instrument, data in response_data.items():
            df = pd.DataFrame(data).set_index('time')
            df.index = pd.DatetimeIndex(df.index)
            df['open'] = df['open'].astype(float)
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            self.data[instrument] = df
