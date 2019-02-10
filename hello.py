import configparser
import json
import pandas as pd
from oandapyV20 import API
from oandapyV20.endpoints import accounts

def main():
    config = configparser.ConfigParser()
    config.read('oanda.cfg')

    ACCOUNT_ID = config['oanda']['account_id']
    API_TOKEN = config['oanda']['account_token']

    api = API(access_token=API_TOKEN)

    req = accounts.AccountInstruments(ACCOUNT_ID)
    res = api.request(req)

    instruments = [i['name'] for i in res['instruments']]
    print(instruments, len(instruments))
if __name__ == "__main__":
    main()