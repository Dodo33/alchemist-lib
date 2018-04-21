
"""

Author: Carniel Giorgio

Strategy description:
Hold a portfolio composed by top 3 assets based on proximity to zero of the linear regression slope.

"""

from alchemist_lib.portfolio import LongsOnlyPortfolio
from alchemist_lib.broker import PoloniexBroker
from alchemist_lib.tradingsystem import TradingSystem
from alchemist_lib.factor import Factor
import alchemist_lib.exchange as exch


def set_weights(df):
    alphas_sum = df["alpha"].sum()

    for asset, alpha in zip(df.index.values, df["alpha"]):
        df.loc[asset, "tmp_weight"] = alphas_sum / alpha
    tmp_weight_sum = df["tmp_weight"].sum()

    for asset, tmp_weight in zip(df.index.values, df["tmp_weight"]):
        df.loc[asset, "weight"] = tmp_weight / tmp_weight_sum
    df.drop(labels = ["tmp_weight"], axis = 1, inplace = True)
    return df


def select_universe(session):
    return exch.get_assets(session = session, exchange_name = "poloniex")


def handle_data(session, universe):
    fct = Factor(session = session)
    prices = fct.history(universe = universe, field = "close", timeframe = "15M", window_length = 30)
    
    reg = fct.LinearRegression(values = prices, window_length = 30)
    df = reg.copy()
    df.rename(columns = {"LinearRegression" : "alpha"}, inplace = True)

    df["alpha"] = df["alpha"].abs()
    df.sort_values(by = ["alpha"], inplace = True)

    df.dropna(inplace = True)
    df = df.head(3)

    return df


algo = TradingSystem(name = "AccumulationZone",
                     portfolio = LongsOnlyPortfolio(capital = 0.03),
                     set_weights = set_weights,
                     select_universe = select_universe,
                     handle_data = handle_data,
                     broker = PoloniexBroker(api_key = "APIKEY",
                                             secret_key = "SECRETKEY"),
                     paper_trading = True)
algo.run(delay = "15M", frequency = 1)








    
