import datetime as dt

from alchemist_lib.datafeed.poloniexdatafeed import PoloniexDataFeed

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker



session = Session()
polo = PoloniexDataFeed(session = session)

assets = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex").all()

tradable_assets = polo.get_assets()
print("Tradable assets: ", tradable_assets)

print("\n")

#Will raise AssertError:
candles = polo.get_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 10), end_date = dt.datetime(2018, 2, 12), timeframe = "3H")

candles = polo.get_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 8), end_date = dt.datetime(2018, 2, 12), timeframe = "1D")
print("Candles 2018-02-08 2018-02-12:\n", candles)

print("\n")

polo.save_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 8), end_date = dt.datetime(2018, 2, 12), timeframe = "1D")
#Another time, to check integrityError exception
polo.save_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 8), end_date = dt.datetime(2018, 2, 12), timeframe = "1D")
print("Candles 2018-02-08 2018-02-12 saved.")

print("\n")

polo.save_last_ohlcv(assets = assets, timeframe = "15M")
print("Last 15m candles saved.\n")

df = polo.get_last_price(assets = assets)
print("Last prices: ", df)

print("\n")

df = polo.get_last_ohlcv(assets = assets, timeframe = "1D")
print("Last daily candles: ", df)

print("\n")

session.close()
