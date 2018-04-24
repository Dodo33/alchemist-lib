import datetime as dt

from sqlalchemy import or_

from alchemist_lib.factor import Factor

import alchemist_lib.utils as utils

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker


session = Session()

fct = Factor(session = session)

assets = session.query(Asset).filter(or_(Asset.ticker == "BCH", Asset.ticker == "ETH", Asset.ticker == "XZC")).all()

print("All assets: ", utils.print_list(assets))
print("\n")

hist = fct.history(assets, "*", "1D", 30)
print("History: ", hist)
print("\n")

reg = fct.LinearRegression(hist, 5, field = "close")
print("Regression 5: ", reg)
print("\n")

ma = fct.MovingAverage(hist["close"], 3)
print("MA 3: ", ma)
print("\n")

sma = fct.SimpleMovingAverage(hist["close"], 3)
print("SMA 3: ", sma)
print("\n")

ema = fct.ExponentialMovingAverage(hist["open"], 3)
print("EMA open 3: ", ema)
print("\n")

mom = fct.Momentum(hist["close"], 3)
print("Momentum 3: ", mom)
print("\n")

roc = fct.RateOfChange(hist["close"], 3)
print("RateOfChange 3: ", roc)
print("\n")

atr = fct.AverageTrueRange(hist, 7)
print("ATR 7: ", atr)
print("\n")

session.close()















