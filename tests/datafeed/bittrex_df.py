import datetime as dt

from alchemist_lib.datafeed.bittrexdatafeed import BittrexDataFeed

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker



session = Session()
bittrex = BittrexDataFeed(session = session)

assets = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "bittrex").all()

tradable_assets = bittrex.get_assets()
print("Tradable assets: ", tradable_assets)

print("\n")

df = bittrex.get_last_price(assets = assets)
print("Last prices: ", df)

print("\n")

candles = bittrex.get_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 8), end_date = dt.datetime(2018, 2, 12), timeframe = "1D")
print("Candles 2018-02-08 2018-02-12:\n", candles)

print("\n")

bittrex.save_ohlcv(assets = assets, start_date = dt.datetime(2018, 2, 8), end_date = dt.datetime(2018, 2, 12), timeframe = "1D")
print("Candles 2018-02-08 2018-02-12 saved.")

print("\n")

bittrex.save_last_ohlcv(assets = assets, timeframe = "1H")
print("Last 1H candles saved.\n")

session.close()
