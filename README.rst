.. image:: https://i.imgur.com/EqWwNDn.png
    :target: https://github.com/Dodo33/alchemist-lib
    :width: 300px
    :height: 150px
    :align: center
    :alt: Alchemist

Alchemist_lib
*************


Description
===========
Alchemist_lib is an automatic trading library for cryptocurrencies that allow to personalize the portfolio based on a specific strategy.


Features
========

 - Easy to use: The interface is similar to `zipline <http://www.zipline.io/>`_, a popular backtesting software for stocks.
 - Portfolio personalization: You can choose the weight of every element on the portfolio.
 - Most common technical analysis indicators already integrated.
 - Execute orders on the most famous exchanges.
 - Possibility to visualize the asset allocation and the portfolio value charts for every strategy thanks to `alchemist-view <https://github.com/Dodo33/alchemist-view>`_.
 - Fully documented and hosted on `readthedocs <http://alchemist-lib.readthedocs.io/en/latest/index.html#>`_.
 

Supported Exchanges
===================
The following exchanges are available to trade on:

    - `Poloniex <https://poloniex.com/>`_
    - `Bittrex <https://bittrex.com/>`_

    
Requirements
============

 - Python3
 - Mysql
    

Installation
============

See the `installing documentation <http://alchemist-lib.readthedocs.io/en/latest/install.html>`_.


Code example
============

Strategy description:
*Hold a portfolio equally composed by Ethereum and BitcoinCash.*

::
    
    from alchemist_lib.portfolio import LongsOnlyPortfolio
    from alchemist_lib.broker import PoloniexBroker
    from alchemist_lib.tradingsystem import TradingSystem
    import alchemist_lib.exchange as exch
    import pandas as pd


    def set_weights(df):
        df["weight"] = 0.5 #Because there are just two assets.
        return df

    def select_universe(session):
        poloniex_assets = exch.get_assets(session = session, exchange_name = "poloniex")

        my_universe = []
        for asset in poloniex_assets:
            if asset.ticker == "ETH" or asset.ticker == "BCH":
                my_universe.append(asset)
        return my_universe

    def handle_data(session, universe):
        #The value of alpha is useless in this case.
        df = pd.DataFrame(data = {"asset" : universe, "alpha" : 0}, columns = ["asset", "alpha"]).set_index("asset")
        return df


    algo = TradingSystem(name = "BuyAndHold",
                         portfolio = LongsOnlyPortfolio(capital = 0.02),
                         set_weights = set_weights,
                         select_universe = select_universe,
                         handle_data = handle_data,
                         broker = PoloniexBroker(api_key = "APIKEY",
                                                 secret_key = "SECRETKEY"),
                         paper_trading = True)
    algo.run(delay = "15M", frequency = 1)



Basic concepts
==============

Alchemist_lib works with three methods:

    - set_weights
    - select_universe
    - handle_data

*set_weights* is used to set the weight that an asset has respect the others within the portfolio. 
The sum of every weight must be close to 1. Must returns a pandas dataframe with two columns: "asset" and "alpha", where "asset" is the index.

*select_universe* filters the assets saved on the database and returns just the ones the strategy will take into consideration.

*handle_data* is the most importat one because it manages the trading logic. Must returns a pandas dataframe with two columns: "asset" and "alpha", where "asset" is the index.

You can find other examples in the ``examples`` directory.


Reporting bugs
==============

A `bug tracker <https://github.com/Dodo33/alchemist-lib/issues>`_ is provided by Github.




        
