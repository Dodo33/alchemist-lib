API Reference
-------------

Trading system
~~~~~~~~~~~~~~

.. autoclass:: alchemist_lib.tradingsystem.TradingSystem
    :members: __init__, set_weights, on_market_open, select_universe, handle_data, rebalance, run
    

Factor
~~~~~~

Factor autoclass

Datafeed
~~~~~~~~

__init__
'''''''''
.. automodule:: alchemist_lib.datafeed
    :members: get_data_sources_dict, get_last_price, save_ohlcv, save_last_ohlcv, check_ohlcv_data

ohlcv
'''''
.. autoclass:: alchemist_lib.datafeed.ohlcv.OhlcvBaseClass
    :members: __init__, _save, save_ohlcv, get_last_ohlcv, save_last_ohlcv

poloniexdatafeed
''''''''''''''''    
.. autoclass:: alchemist_lib.datafeed.poloniexdatafeed.PoloniexDataFeed
    :members: __init__, get_assets, get_last_price, get_ohlcv

bittrexdatafeed
'''''''''''''''
.. autoclass:: alchemist_lib.datafeed.bittrexdatafeed.BittrexDataFeed
    :members: __init__, get_assets, get_last_price, get_ohlcv
    
Broker
~~~~~~

broker
''''''
.. autoclass:: alchemist_lib.broker.broker.BrokerBaseClass
    :members: __init__, set_session, execute

poloniexbroker
''''''''''''''
.. autoclass:: alchemist_lib.broker.poloniexbroker.PoloniexBroker
    :members: __init__, place_order

bittrexbroker
'''''''''''''
.. autoclass:: alchemist_lib.broker.bittrexbroker.BittrexBroker
    :members: __init__, place_order

Portfolio
~~~~~~~~~

portfolio
'''''''''
.. autoclass:: alchemist_lib.portfolio.portfolio.PortfolioBaseClass
    :members: __init__, rebalance, load_ptf

longsonly
'''''''''
.. autoclass:: alchemist_lib.portfolio.longsonly.LongsOnlyPortfolio
    :members: __init__, set_allocation

Exchange
~~~~~~~~

exchange
''''''''
.. autoclass:: alchemist_lib.exchange.exchange.ExchangeBaseClass
    :members: __init__

__init__
''''''''
.. automodule:: alchemist_lib.exchange
    :members: get_exchanges_dict, are_tradable, get_assets

poloniexexchange
''''''''''''''''
.. autoclass:: alchemist_lib.exchange.poloniexexchange.PoloniexExchange
    :members: __init__, are_tradable, get_min_order_size

bittrexexchange
'''''''''''''''
.. autoclass:: alchemist_lib.exchange.bittrexexchange.BittrexExchange
    :members: __init__, are_tradable, get_min_order_size

Populate
~~~~~~~~

saver
'''''
.. autoclass:: alchemist_lib.populate.saver.Saver
    :members: __init__, _save, instrument, timeframe, broker, data_source, timetable, exchange, asset

populate
''''''''
.. autoclass:: alchemist_lib.populate.populate.PopulateBaseClass
    :members: __init__

__init__
''''''''
.. autoclass:: alchemist_lib.populate
    :members: get_populate_dict, populate_all, update_asset_list

poloniexpopulate
''''''''''''''''
.. autoclass:: alchemist_lib.populate.poloniexpopulate.PoloniexPopulate
    :members: __init__, get_exchange_instance, populate, update_asset_list

bittrexpopulate
'''''''''''''''
.. autoclass:: alchemist_lib.populate.bittrexpopulate.BittrexPopulate
    :members: __init__, get_exchange_instance, populate, update_asset_list














