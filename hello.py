import configparser 
import oandapy as opy
import pandas as pd

def main():
    config = configparser.ConfigParser()
    config.read('oanda.cfg')

    ACCOUNT_ID = config['oanda']['account_id']
    #
    # The config object is initialized by the argument parser, and contains
    # the REST APID host, port, accountID, etc.
    #

    api = opy.APIv20(environment='practice',
                access_token=config['oanda']['account_token'])

    instruments = api.account.get_instruments(ACCOUNT_ID)
    print(instruments)
    #
    # Fetch the tradeable instruments for the Account found in the config file
    #
    # response = oanda.account..instruments(account_id)

    # #
    # # Extract the list of Instruments from the response.
    # #
    # instruments = response.get("instruments", "200")

    # instruments.sort(key=lambda i: i.name)

    # def marginFmt(instrument):
    #     return "{:.0f}:1 ({})".format(
    #         1.0 / float(instrument.marginRate),
    #         instrument.marginRate
    #     )

    # def pipFmt(instrument):
    #     location = float(10 ** instrument.pipLocation)
    #     return "{:.4f}".format (location)

    # #
    # # Print the details of the Account's tradeable instruments
    # #
    # common.view.print_collection(
    #     "{} Instruments".format(len(instruments)),
    #     instruments,
    #     [
    #         ("Name", lambda i: i.name),
    #         ("Type", lambda i: i.type),
    #         ("Pip", pipFmt),
    #         ("Margin Rate", marginFmt),
    #     ]
    # )

if __name__ == "__main__":
    main()