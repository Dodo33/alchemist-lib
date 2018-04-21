from alchemist_lib.exchange import PoloniexExchange

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker
from alchemist_lib.database.timeframe import Timeframe



session = Session()
polo = PoloniexExchange()

assets = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex").all()
print("All assets in db: ", assets)

print("\n")

for asset in assets:
    min_trade_size = polo.get_min_trade_size(asset)
    print("The min order size for ", asset.ticker, " is ", min_trade_size)

print("\n")

tradable = polo.are_tradable(assets = assets)
print("All tradable assets: ", tradable)

