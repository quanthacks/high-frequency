import alpaca_trade_api as tradeapi
import configparser

config = configparser.ConfigParser()
config.read('alpaca.cfg')

api = tradeapi.REST(config['alpaca']['key_id'], config['alpaca']['secret_key'], base_url="https://paper-api.alpaca.markets")

account = api.get_account()
print(account)

print(api.get_asset("USD"))