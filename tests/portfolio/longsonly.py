import pandas as pd

import random

from decimal import Decimal

import numpy as np

import alchemist_lib.utils as utils

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker
from alchemist_lib.database.ts import Ts
from alchemist_lib.database.timeframe import Timeframe

from alchemist_lib.portfolio.longsonly import LongsOnlyPortfolio

import alchemist_lib.datafeed as dfeed



def set_weights(df):
    alphas_sum = df["alpha"].sum()

    df["weight"] = np.nan
    for asset, alpha in zip(df.index.values, df["alpha"]):
        df.loc[asset, "weight"] = alpha / alphas_sum

    return df


session = Session()

assets = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex",
                                                                     Asset.ticker.in_(["ETH", "BCH", "LTC"])).all()
print("Assets: ", utils.print_list(assets), "\n")

df = pd.DataFrame(data = {"asset" : assets}, columns = ["asset", "alpha"]).set_index("asset")
for asset in df.index.values:
    df.loc[asset, "alpha"] = Decimal(random.uniform(0.5, 5.0))
df.sort_values(by = ["alpha"], inplace = True)

print("Random alphas: ", df)

print("\n\n")

ptf = LongsOnlyPortfolio(capital = 0.5)

df = set_weights(df = df)
print("Random alphas with weights: ", df)

print("\n\n")

prices = dfeed.get_last_price(assets = assets)
print("Last prices: ", prices)

print("\n\n")

target_allocs = ptf.set_allocation(session = session, name = "AccumulationZone", df = df)
print("Allocations: ", utils.print_list(target_allocs))

print("\n")

balance = Decimal(0)
for alloc in target_allocs:
    print(alloc.ticker, "\t", alloc.amount, "\t", prices.loc[alloc.asset, "last_price"])
    balance += (alloc.amount * prices.loc[alloc.asset, "last_price"])

print("\nFinal balance: ", balance)

print("\n###########################################################\n")

ptf.capital = 0.75

df = pd.DataFrame(data = {"asset" : assets}, columns = ["asset", "alpha"]).set_index("asset")
for asset in df.index.values:
    df.loc[asset, "alpha"] = Decimal(random.uniform(0.5, 5.0))
df.sort_values(by = ["alpha"], inplace = True)

print("Random alphas: ", df)

print("\n\n")

df = set_weights(df = df)
print("Random alphas with weights: ", df)

print("\n")

curr_ptf = target_allocs
target_ptf = ptf.set_allocation(session = session, name = "AccumulationZone", df = df)

print("Current ptf: ", utils.print_list(curr_ptf), "\n")
print("Target ptf: ", utils.print_list(target_ptf), "\n")

print("\n")

orders = ptf.rebalance(curr_ptf = curr_ptf, target_ptf = target_ptf)
print("Orders to execute: ", utils.print_list(orders))

session.close()
