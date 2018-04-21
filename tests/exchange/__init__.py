import alchemist_lib.exchange as exchange

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker
from alchemist_lib.database.timeframe import Timeframe



session = Session()

assets = session.query(Asset).join(Instrument, Asset.instrument).filter(Instrument.instrument_type == "cryptocurrency").all()
print("All assets in db: ", assets)

print("\n")

tradable = exchange.are_tradable(assets = assets, exchange_name = "poloniex")
print("All tradable assets on Poloniex: ", tradable)

print("\n")

all_assets = exchange.get_assets(session = session, exchange_name = "bittrex")
print("All assets on Bittrex: ", all_assets)

session.close()

