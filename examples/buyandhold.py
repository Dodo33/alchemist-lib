
"""

Author: Carniel Giorgio

Strategy description:
Hold a portfolio equally composed by Ethereum and BitcoinCash.

"""

from alchemist_lib.portfolio import LongsOnlyPortfolio
from alchemist_lib.broker import PoloniexBroker
from alchemist_lib.tradingsystem import TradingSystem
import alchemist_lib.exchange as exch
import pandas as pd


def set_weights(df):
    df["weight"] = 0.5 #Because there are just two assets.
    return df

def select_universe(session):
    poloniex_assets = exch.get_assets(session = session, exchange_name = "poloniex")

    my_universe = []
    for asset in poloniex_assets:
        if asset.ticker == "ETH" or asset.ticker == "BCH":
            my_universe.append(asset)
    return my_universe

def handle_data(session, universe):
    #The value of alpha is useless in this case.
    df = pd.DataFrame(data = {"asset" : universe, "alpha" : 0}, columns = ["asset", "alpha"]).set_index("asset")
    return df


algo = TradingSystem(name = "BuyAndHold",
                     portfolio = LongsOnlyPortfolio(capital = 0.02),
                     set_weights = set_weights,
                     select_universe = select_universe,
                     handle_data = handle_data,
                     broker = PoloniexBroker(api_key = "APIKEY",
                                             secret_key = "SECRETKEY"),
                     paper_trading = True)
algo.run(delay = "15M", frequency = 1)








    
