import datetime as dt

import alchemist_lib.datafeed as dfeed

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker



session = Session()
assets = session.query(Asset).all()

print("All assets: ", assets)

print("\n")

last_prices = dfeed.get_last_price(assets = assets)
print("Last prices: ", last_prices)

print("\n")

dfeed.save_ohlcv(session = session, assets = assets, start_date = dt.datetime(2018,2,1), timeframe = "1D")
print("OHLCV from 2018-02-01 saved!")

print("\n")

dfeed.save_last_ohlcv(session = session, assets = assets, timeframe = "1D")
print("Last OHLCV saved!")

session.close()
