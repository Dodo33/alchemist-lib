
"""

Author: Carniel Giorgio

Strategy description:
Hold a portfolio composed by top 5 assets by volume whose EMA 10 is above the EMA 21. Rebalance it every hour.

"""

from alchemist_lib.portfolio import LongsOnlyPortfolio
from alchemist_lib.broker import BittrexBroker
from alchemist_lib.tradingsystem import TradingSystem
from alchemist_lib.factor import Factor
import pandas as pd
import alchemist_lib.exchange as exch


def set_weights(df):
    alphas_sum = df["alpha"].sum()
    for asset, alpha in zip(df.index.values, df["alpha"]):
        df.loc[asset, "weight"] = alpha / alphas_sum
        
    return df

def select_universe(session):
    return exch.get_assets(session = session, exchange_name = "bittrex")

def handle_data(session, universe):
    fct = Factor(session = session)
    prices = fct.history(universe = universe, field = "close", timeframe = "1H", window_length = 21)
    
    ema10 = fct.ExponentialMovingAverage(values = prices, window_length = 10, field = "close").rename(columns = {"ExponentialMovingAverage" : "ema10"})
    ema21 = fct.ExponentialMovingAverage(values = prices, window_length = 21, field = "close").rename(columns = {"ExponentialMovingAverage" : "ema21"})

    concated = pd.concat([ema10, ema21], axis = 1)
    concated = concated.loc[concated["ema10"] > concated["ema21"], :]
    
    vol = fct.history(universe = concated.index.values, field = "volume", timeframe = "1H", window_length = 1)

    df = pd.concat([concated, vol], axis = 1)
    
    df = df[["volume"]].rename(columns = {"volume" : "alpha"})
    
    if len(df) > 5:
        df = df.sort_values(by = "alpha", ascending = False)
        df = df.head(5)
        
    return df


algo = TradingSystem(name = "MovingAverageCrossover",
                     portfolio = LongsOnlyPortfolio(capital = 0.05),
                     set_weights = set_weights,
                     select_universe = select_universe,
                     handle_data = handle_data,
                     broker = BittrexBroker(api_key = "APIKEY",
                                            secret_key = "SECRETKEY"),
                     paper_trading = True)
algo.run(delay = "1H", frequency = 1)
