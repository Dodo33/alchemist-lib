.. image:: https://i.imgur.com/EqWwNDn.png
    :target: https://github.com/Dodo33/alchemist-lib
    :width: 212px
    :align: center
    :alt: Alchemist

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

Installing with ``pip``:
------------------------
If python3-pip is already installed::
        
    $ pip3 install alchemist_lib
        
If you don't have pip installed, you can easily install it by downloading and running `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_.
    
Cloning the repository with ``git``:
------------------------------------
If git is already installed::
        
    $ git clone https://github.com/Dodo33/alchemist-lib
    $ cd alchemist-lib
    $ python3 setup.py install


After the installation it's important to specify mysql credentials::

    $ sudo alchemist populate -l "hostname" -u "username" -p "password" -d "database_name"



Code example
============

The following strategy will analyse the trend for every cryptocurrency traded on Poloniex based on the slope of the linear regression.
It buys the top 5 assets whose slope is closed to zero. The more the slope is close to zero, the more weight the asset gets within the portfolio.
The procedure is repeated every 15 minutes.

::
    
    from alchemist_lib.portfolio import LongsOnlyPortfolio
    from alchemist_lib.broker import PoloniexBroker
    from alchemist_lib.tradingsystem import TradingSystem
    from alchemist_lib.factor import Factor
    import alchemist_lib.exchange as exch


    def set_weights(df):
        alphas_sum = df["alpha"].sum()

        for asset, alpha in zip(df.index.values, df["alpha"]):
            df.loc[asset, "tmp_weight"] = alphas_sum / alpha
        tmp_weight_sum = df["tmp_weight"].sum()

        for asset, tmp_weight in zip(df.index.values, df["tmp_weight"]):
            df.loc[asset, "weight"] = tmp_weight / tmp_weight_sum
        df.drop(labels = ["tmp_weight"], axis = 1, inplace = True)
        return df


    def select_universe(session):
        return exch.get_assets(session = session, exchange_name = "poloniex")


    def handle_data(session, universe):
        fct = Factor(session = session)
        prices = fct.history(universe = universe, field = "close", timeframe = "15M", window_length = 30)
        
        reg = fct.LinearRegression(values = prices, window_length = 30)
        df = reg.copy()
        df.rename(columns = {"LinearRegression" : "alpha"}, inplace = True)

        df["alpha"] = df["alpha"].abs()
        df.sort_values(by = ["alpha"], inplace = True)

        df.dropna(inplace = True)
        df = df.head(5)

        print("To invest in: ", df, "\n")
        return df


    algo = TradingSystem(name = "AccumulationZone",
                         portfolio = LongsOnlyPortfolio(capital = 0.1),
                         set_weights = set_weights,
                         select_universe = select_universe,
                         handle_data = handle_data,
                         broker = PoloniexBroker(api_key = "APIKEY",
                                                 secret_key = "SECRETKEY"),
                         test = True)
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




        
