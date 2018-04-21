from alchemist_lib.database import Session

from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.aum_history import AumHistory
from alchemist_lib.database.ohlcv import Ohlcv
from alchemist_lib.database.ptf_allocation import PtfAllocation
from alchemist_lib.database.ts import Ts
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker
from alchemist_lib.database.timeframe import Timeframe
from alchemist_lib.database.executed_order import ExecutedOrder



session = Session()

all_assets = session.query(Asset).all()
bittrex_assets = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "Bittrex").all()
print("All assets:\n", all_assets)
print("All assets instrument:\n", [asset.instrument for asset in all_assets])
print("All assets exchanges:\n", [asset.exchanges for asset in all_assets])
print("Bittrex assets:\n", bittrex_assets)

print("\n")

aum_history = session.query(AumHistory).all()
print("All aum history:\n", aum_history)
print("All aum history trading systems:\n", [aum_record.ts for aum_record in aum_history])

print("\n")

exchanges = session.query(Exchange).all()
print("All exchanges:\n", exchanges)
print("All exchanges data source:\n", [exchange.price_data_source for exchange in exchanges])
print("All exchanges timetable:\n", [exchange.timetable for exchange in exchanges])
print("All exchanges calendar:\n", [exchange.brokers for exchange in exchanges])

print("\n")

instruments = session.query(Instrument).all()
print("All instruments:\n", instruments)

print("\n")

all_ohlcv = session.query(Ohlcv).all()
print("All ohlcv:\n", all_ohlcv)
print("All assets on ohlcv:\n", [ohlcv.asset for ohlcv in all_ohlcv])

print("\n")

all_allocations = session.query(PtfAllocation).all()
print("All allocations:\n", [str(alloc) for alloc in all_allocations])
print("All allocations:\n", [repr(alloc) for alloc in all_allocations])

print("All assets on allocations:\n", [alloc.asset for alloc in all_allocations])
print("All ts on allocations:\n", [alloc.ts for alloc in all_allocations])

print("\n")

tradingsystems = session.query(Ts).all()
print("All ts:\n", tradingsystems)

print("\n")

timetables = session.query(Timetable).all()
print("All timetables:\n", timetables)

print("\n")

datasources = session.query(PriceDataSource).all()
print("All datasources:\n", datasources)
print("All timeframe per datasource: ", [ds.available_timeframes for ds in datasources])

print("\n")

brokers = session.query(Broker).all()
print("All brokers:\n", brokers)

print("\n")

timeframes = session.query(Timeframe).all()
print("All timeframes:\n", timeframes)

print("\n")

orders = session.query(ExecutedOrder).all()
print("All orders:\n", orders)
print("Exchange for order:\n", [order.exchange for order in orders])
print("Asset for order:\n", [order.asset for order in orders])
print("Broker for order:\n", [order.broker for order in orders])

session.close()












