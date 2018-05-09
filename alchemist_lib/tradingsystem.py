from abc import ABC, abstractmethod

import datetime as dt

import logging

import pandas as pd

from decimal import Decimal

import time

from apscheduler.schedulers.blocking import  BlockingScheduler

from sqlalchemy import exc

from . import datafeed

from . import utils

from . import order

from .database import Session
from .database.asset import Asset
from .database.instrument import Instrument
from .database.timetable import Timetable
from .database.broker import Broker
from .database.ts import Ts
from .database.ptf_allocation import PtfAllocation



class TradingSystem():

    """
    Basic class for every trading system.
    The run method will start the live-trading.

    Attributes:
        name (str): The name of the trading system.
        portfolio (alchemist_lib.portfolio.*): An istance of a portfolio class.
        broker (alchemist_lib.broker.*): An instance of a module in alchemist_lib.broker package.
        _set_weights (callable): The function to set the weights of every asset in the portfolio.
        _select_universe (callable): The function to select the universe of asset.
        _handle_data (callable): The function to manage the trading logic.
        paper_trading (boolean): If this arg is True no orders will be executed, they will be just printed and saved.
        rebalance_time (int): Autoincrement number, used to manage the frequency of rebalancing.
        session (sqlalchemy.orm.session.Session): Connection to the database.
    """
    
    def __init__(self, name, portfolio, set_weights, select_universe, handle_data, broker, paper_trading = False):

        """
        Costructor method.
        After setting the attributes it will register the trading system in the database.

        Args:
            name (str): Name of the trading system.
            portfolio (alchemist_lib.portfolio.*): An istance of a portfolio class.
            broker (alchemist_lib.broker.*): An instance of a module in alchemist_lib.broker package.
            set_weights (callable): The function to set the weights of every asset in the portfolio.
            select_universe (callable): The function to select the universe of asset.
            handle_data (callable): The function to manage the trading logic.
            paper_trading (boolean, optional): Specify if the trading system has to execute orders or just simulate.
        """
        
        assert isinstance(name, str), "The name of the trading system must be a string (str)."

        #https://docs.python.org/3/library/logging.handlers.html
        file_handler = logging.FileHandler(filename = "{}.log".format(name), mode = "w")
        #console_handler = logging.StreamHandler()
        #console_handler.setLevel(level = logging.INFO)
        #console_handler.setFormatter(logging.Formatter('%(asctime)s : %(message)s'))
        
        logging.basicConfig(handlers = [
                                file_handler,
                                #console_handler,
                            ],
                            level = logging.DEBUG,
                            format = '%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                            datefmt = '%m/%d/%Y %I:%M:%S')
        logging.Formatter.converter = time.gmtime

        logging.info("Started.")
        print(utils.now(), ": Started.")
        
        self.name = name
        self.portfolio = portfolio
        self.broker = broker

        self._set_weights = set_weights
        self._select_universe = select_universe
        self._handle_data = handle_data

        self.paper_trading = paper_trading
        
        self.rebalance_time = 0

        self.session = Session()

        self.broker.set_session(session = self.session)

        self.scheduler = BlockingScheduler()
        
        ts = Ts(ts_name = self.name,
                datetime_added = dt.datetime.utcnow(),
                aum = self.portfolio.capital,
                ptf_type = type(self.portfolio).__name__
                )

        logging.debug("Saving the trading system {}.".format(self.name))
        try:
            self.session.add(ts)
            self.session.commit()
        except exc.IntegrityError:
            self.session.rollback()
            logging.warning("Trading system already present.")
            print(utils.now(), ": Trading system already present.")

            self.session.query(Ts).filter(Ts.ts_name == self.name).update({"datetime_added" : ts.datetime_added,
                                                                           "ptf_type" : ts.ptf_type
                                                                           })
            self.session.commit()
            


    def set_weights(self, df):

        """
        Call the _set_weights callable attribute if it's not None.

        Args:
            df (pandas.DataFrame): The alpha dataframe setted in handle_data().

        Returns:
            weights (pandas.DataFrame): Return a dataframe with a weight for every asset. Empty if _set_weights is None.
        """
        
        if self._set_weights == None:
            loggin.warning("_set_weights is None.")
            print(utils.now(), ": _set_weights is None.")
            return pd.DataFrame(columns = ["asset", "alpha", "weight"]).set_index("asset")
        
        weights = self._set_weights(df = df)

        if isinstance(weights, pd.DataFrame) == False:
            raise Exception("The set_weight function must return a pandas.DataFrame!")

        if "weight" not in weights.columns:
            raise Exception("The set_weight function must have a column called 'weight'!")

        weights_sum = weights["weight"].sum()
        if weights_sum < 0.9 or weights_sum > 1.1:
            raise Exception("The sum of the weights returned by the set_weights function must be near 1.0!")
        
        return weights

    
    def on_market_open(self, timeframe, frequency, universe):

        """
        Save new data and call the rebalance function.

        Args:
            timeframe (str): The timeframe we want to collect informations about for every asset in the universe.
            frequency (int): Frequency of rebalancing.
        """

        
        
        logging.info("--------------------------------------------------")
        print("--------------------------------------------------")
        
        start_time = time.time()
        datafeed.save_last_ohlcv(session = self.session, assets = universe, timeframe = timeframe)
        end_time = time.time()

        delta_time = round(end_time - start_time, 2)
        logging.info("Last OHLCV data retrived in {} seconds.".format(delta_time))
        print(utils.now(), ": Last OHLCV data retrived in {} seconds.".format(delta_time))
        
        self.rebalance(alphas = self.handle_data(universe = universe), orders_type = order.MARKET, frequency = frequency)


    def select_universe(self):

        """
        Call the _select_universe callable attribute if it's not None.

        Returns:
            universe (list[alchemist_lib.database.Asset.asset]): Return a list of assets.
        """
        
        if self._select_universe == None:
            logging.warning("_select_universe is None.")
            print(utils.now(), ": _select_universe is None.")
            return []
        
        universe = self._select_universe(session = self.session)

        if isinstance(universe, list) == False:
            raise Exception("The select_universe function must returns a list!")

        if len(universe) <= 0:
            raise Exception("The select_universe must not returns an empty list!")

        for asset in universe:
            if isinstance(asset, Asset) == False:
                raise Exception("The select_universe function has returned a list composed by somthing that is not an Asset!")
            
        return utils.to_list(universe)
    

    def handle_data(self, universe):

        """
        Call the _handle_data callable attribute if it's not None.

        Returns:
            data (pandas.DataFrame): Return a dataframe with an alpha value for every asset. Empty if _handle_data is None.
        """
        
        if self._handle_data == None:
            logging.warning("_handle_data is None.")
            print(utils.now(), ": _handle_data is None.")
            return pd.DataFrame(columns = ["asset", "alpha"]).set_index("alpha")

        start_time = time.time()
        
        data = self._handle_data(session = self.session, universe = universe)

        if isinstance(data, pd.DataFrame) == False:
            raise Exception("The handle_data function must return a pandas.DataFrame!")

        if "asset" not in list(data.index.names):
            raise Exception("The handle_data function must have the index called 'asset'!")
        
        if "alpha" not in data.columns:
            raise Exception("The handle_data function must have a column called 'alpha'!")

        data.dropna(inplace = True)

        end_time = time.time()

        delta_time = round(end_time - start_time, 2)
        logging.info("The handle_data function was executed in {} seconds.".format(delta_time))
        print(utils.now(), ": The handle_data function was executed in {} seconds.".format(delta_time))
        
        return data


    def rebalance(self, alphas, orders_type, frequency):

        """
        This method rebalance the portfolio based on the alphas parameters. It also update the current AUM value on the database.

        Args:
            alphas (pandas.DataFrame): A dataframe with the following columns:
                * asset (alchemist_lib.database.asset.Asset): Must be the index.
                * alpha (decimal.Decimal): The value that will be used to calculate the weight of the asset within the portfolio.
            orders_type (str): Order type identifier.
            frequency (int): Frequency of rebalancing.
        """

        logging.debug("Rebalance start datetime: {}".format(dt.datetime.utcnow()))
        
        start_time = time.time()
        
        curr_ptf = self.portfolio.load_ptf(session = self.session, name = self.name)
        if len(curr_ptf) == 0:
            cryptocurrency_id = self.session.query(Instrument).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
            curr_ptf.append(PtfAllocation(ticker = "BTC",
                                          instrument_id = cryptocurrency_id,
                                          amount = self.portfolio.capital,
                                          base_currency_amount = self.portfolio.capital,
                                          ts_name = self.name))
        
        logging.info("Current portfolio: {}".format(utils.print_list(curr_ptf)))
        print(utils.now(), ": Current portfolio: {}".format(utils.print_list(curr_ptf)))
        
        if self.rebalance_time % frequency == 0:
            logging.debug("It's rebalance time.")
            
            aum = self.session.query(Ts).filter(Ts.ts_name == self.name).one().aum
            self.portfolio.capital = aum

            logging.debug("The aum is {}.".format(aum))

            target_ptf_df  = self.set_weights(df = alphas)
            target_ptf = self.portfolio.set_allocation(session = self.session, name = self.name, df = target_ptf_df)

            logging.info("Target portfolio: {}".format(utils.print_list(target_ptf)))
            print(utils.now(), ": Target portfolio: {}".format(utils.print_list(target_ptf)))
            
            orders_allocs = self.portfolio.rebalance(curr_ptf = curr_ptf, target_ptf = target_ptf)

            logging.debug("Orders to execute to get the ideal portfolio: {}".format(utils.print_list(orders_allocs)))

            if self.paper_trading:
                new_target_ptf = target_ptf
            else:
                new_target_ptf = self.broker.execute(allocs = orders_allocs, orders_type = orders_type, ts_name = self.name, curr_ptf = curr_ptf)
                logging.info("Result of orders execution: {}".format(utils.print_list(new_target_ptf)))
                print(utils.now(), ": Result of orders execution: {}".format(utils.print_list(new_target_ptf)))
            
            try:
                self.session.query(PtfAllocation).filter(PtfAllocation.ts_name == self.name).delete()
                self.session.add_all(new_target_ptf)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logging.error("An exception occurs on the transaction on the rebalance function.")
                logging.exception("Exception: {}".format(e))
                print(utils.now(), ": An exception occurs on the transaction on the rebalance function.") 
                raise
            
            curr_ptf = new_target_ptf


        last_price = datafeed.get_last_price(assets = [alloc.asset for alloc in curr_ptf])
        new_aum = Decimal(0)
        for alloc in curr_ptf:
            if alloc.ticker == "BTC":
                new_aum += alloc.amount
            else:
                new_aum += (abs(alloc.amount) * last_price.loc[alloc.asset, "last_price"])

        logging.debug("The new aum is {}".format(new_aum))
        print(utils.now(), "Assets under management: {}".format(round(new_aum, 8)))
        
        self.session.query(Ts).filter(Ts.ts_name == self.name).update({"aum" : new_aum})
        self.session.commit()

        self.rebalance_time += 1

        end_time = time.time()

        delta_time = round(end_time - start_time, 2)
        
        logging.info("The rebalance function was executed in {} seconds.".format(delta_time))
        print(utils.now(), ": The rebalance function was executed in {} seconds.".format(delta_time))


    def run(self, delay, frequency):
        
        """
        This method manages the "event-driven" interface. Start every method at the right time.

        Args:
            delay (str): Timeframe identifier. Every delay time the on_market_open is executed.
            frequency (int): Frequency of rebalancing.

        """
        
        assert frequency > 0, "The frequency must be > 0."

        universe = self.select_universe()
        
        instrument_timetable = {}
        for asset in universe:
            if asset.instrument not in list(instrument_timetable.keys()):
                instrument_timetable[asset.instrument] = asset.exchanges[0].timetable
        
        for instrument, timetable in instrument_timetable.items():
            if timetable == None:
                time_expression = utils.execution_time_str(timetable = timetable, delay = delay)
                logging.debug("Time expressione for add_job(): {}".format(time_expression))
                self.scheduler.add_job(func = self.on_market_open, kwargs = {"timeframe" : delay, "frequency" : frequency, "universe" : universe}, max_instances = 10, **time_expression)
            else:
                logging.critical("Timetable is not None. NotImplemented raised.")
                raise NotImplemented("Timetable is not None. NotImplemented raised.")
        self.scheduler.start()
        
        """
        self.on_market_open(timeframe = delay, frequency = frequency)
        print("######################################################")
        self.on_market_open(timeframe = delay, frequency = frequency)
        """













        
