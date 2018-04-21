import alchemist_lib.order as order

from decimal import Decimal

from alchemist_lib.broker import PoloniexBroker

import alchemist_lib.utils as utils

from alchemist_lib.database import Session
from alchemist_lib.database.asset import Asset
from alchemist_lib.database.exchange import Exchange
from alchemist_lib.database.instrument import Instrument
from alchemist_lib.database.price_data_source import PriceDataSource
from alchemist_lib.database.timetable import Timetable
from alchemist_lib.database.broker import Broker
from alchemist_lib.database.timeframe import Timeframe
from alchemist_lib.database.ptf_allocation import PtfAllocation

from alchemist_lib.portfolio import LongsOnlyPortfolio

import alchemist_lib.datafeed as dfeed



session = Session()

ptf = LongsOnlyPortfolio(capital = 0.05)

ts_name = "AccumulationZone"

BTC = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex", Asset.ticker == "BTC").one()
ETH = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex", Asset.ticker == "ETH").one()
LTC = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex", Asset.ticker == "LTC").one()
BCH = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex", Asset.ticker == "BCH").one()

poloniex = PoloniexBroker(api_key = "APIKEY",
                          secret_key = "SECRETKEY")
poloniex.set_session(session = session)


ptf_t0 = []
ptf_t1 = [
          PtfAllocation(ticker = BTC.ticker,
                        instrument_id = BTC.instrument_id,
                        amount = -ptf.capital,
                        base_currency_amount = -ptf.capital,
                        ts_name = ts_name),
          PtfAllocation(ticker = ETH.ticker,
                        instrument_id = ETH.instrument_id,
                        amount = 0.0,
                        base_currency_amount = 0,
                        ts_name = ts_name),
          PtfAllocation(ticker = LTC.ticker,
                        instrument_id = LTC.instrument_id,
                        amount = 0.0,
                        base_currency_amount = 0,
                        ts_name = ts_name),
          PtfAllocation(ticker = BCH.ticker,
                        instrument_id = BCH.instrument_id,
                        amount = 0.0,
                        base_currency_amount = 0,
                        ts_name = ts_name)
          ]

for alloc in ptf_t1:
    if alloc.ticker == "BTC":
        alloc.asset = BTC
    if alloc.ticker == "ETH":
        alloc.asset = ETH
    elif alloc.ticker == "LTC":
        alloc.asset = LTC
    elif alloc.ticker == "BCH":
        alloc.asset = BCH

prices = dfeed.get_last_price(assets = [alloc.asset for alloc in ptf_t1])

for alloc in ptf_t1:
    if alloc.ticker != "BTC":
        alloc.base_currency_amount = ptf.capital / 3
        alloc.amount = Decimal(alloc.base_currency_amount) / prices.loc[alloc.asset, "last_price"]

executed_orders = poloniex.execute(allocs = ptf_t1, ts_name = ts_name, orders_type = order.MARKET, curr_ptf = ptf_t0)

print("Executed order for ptf_t1: ", utils.print_list(executed_orders))

ptf_t1 = executed_orders


print("-----------------------------------------------------")


ptf_t2 = [
          PtfAllocation(ticker = ETH.ticker,
                        instrument_id = ETH.instrument_id,
                        amount = 0.0,
                        base_currency_amount = 0,
                        ts_name = ts_name),
          PtfAllocation(ticker = LTC.ticker,
                        instrument_id = LTC.instrument_id,
                        amount = 0.0,
                        base_currency_amount = 0,
                        ts_name = ts_name)
         ]

for alloc in ptf_t2:
    if alloc.ticker == "BTC":
        alloc.asset = BTC
    if alloc.ticker == "ETH":
        alloc.asset = ETH
    elif alloc.ticker == "LTC":
        alloc.asset = LTC
    elif alloc.ticker == "BCH":
        alloc.asset = BCH

prices = dfeed.get_last_price(assets = [alloc.asset for alloc in ptf_t2])

for alloc in ptf_t2:
    if alloc.ticker != "BTC":
        alloc.base_currency_amount = ptf.capital / 2
        alloc.amount = Decimal(alloc.base_currency_amount) / prices.loc[alloc.asset, "last_price"]


orders_to_exec = ptf.rebalance(curr_ptf = executed_orders, target_ptf = ptf_t2)
print("Orders to execute: ", utils.print_list(orders_to_exec))

executed_orders = poloniex.execute(allocs = orders_to_exec, ts_name = ts_name, orders_type = order.MARKET, curr_ptf = executed_orders)

print("Executed order for ptf_t2: ", utils.print_list(executed_orders))

print("-----------------------------------------------------")

session.close()

















          
