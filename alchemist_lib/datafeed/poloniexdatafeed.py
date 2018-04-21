from poloniex import Poloniex, PoloniexError

import pandas as pd

import datetime as dt

import time

from decimal import Decimal

from .ohlcv import OhlcvBaseClass

from ..database.ohlcv import Ohlcv
from ..database.price_data_source import PriceDataSource
from ..database.timeframe import Timeframe
from ..database.asset import Asset
from ..database.instrument import Instrument

from .. import utils

import logging



class PoloniexDataFeed(OhlcvBaseClass):


    """
    Class that collects data from Poloniex.
    Inherits from alchemist_lib.datafeed.ohlcv.OhlcvBaseClass.

    Website: https://poloniex.com/

    Api documentation: https://poloniex.com/support/api/

    Api wrapper: https://github.com/s4w3d0ff/python-poloniex

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
        polo (poloniex.Poloniex): Communication object.
    """
    
    sleep_seconds = 0.5

    
    def __init__(self, session):

        """
        Costructor method.

        Args:
            session (sqlalchemy.orm.session.Session): Connection to the database.
        """
        
        OhlcvBaseClass.__init__(self, session = session)
        self.polo = Poloniex()


    def get_last_price(self, assets):

        """
        Retrieves last trade price of the list of assets. 

        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want the last trade price of.

        Return:
            df (pandas.DataFrame): A dataframe with the following columns:
                * asset (alchemist_lib.database.asset.Asset): Must be the index.
                * last_price (decimal.Decimal): The last price of the associated asset.
            If some prices are not retrieved the last_price attribute will be 0.
        """
        
        assets = utils.to_list(assets)

        tickers = self.polo.returnTicker()
        
        df = pd.DataFrame(data = {"asset" : assets, "last_price" : Decimal(0)}, columns = ["asset", "last_price"]).set_index("asset")
        for asset in assets:
            if "BTC_{}".format(asset.ticker) in tickers:
                df.loc[asset, "last_price"] = Decimal(tickers["BTC_{}".format(asset.ticker)]["last"])
                logging.debug("{} last price: {}".format(asset.ticker, df.loc[asset, "last_price"]))

        return df


    def get_assets(self):
        
        """
        Returns the list of assets traded.

        Return:
            assets (list[alchemist_lib.database.asset.Asset]): List of assets.

        Note:
            Return only pairs with bitcoin as base currency.
        """
        
        tickers = self.polo.returnTicker()

        cryptocurrency_id = self.session.query(Instrument.instrument_id).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
        
        assets = []
        for pair in list(tickers.keys()):
            splitted_pair = pair.split("_")
            if splitted_pair[0] == "BTC":
                asset = Asset(ticker = splitted_pair[1], instrument_id = cryptocurrency_id, name = None)
                assets.append(asset)
                
        return assets
        
    

    def get_ohlcv(self, assets, start_date, timeframe, end_date = dt.datetime.utcnow()):

        """
        Collects ohlcv data from start_date to end_date for every asset.

        Args:
            assets (list[alchemist_lib.database.asset.Asset]): List of assets.
            start_date (datetime.datetime): Datetime to start collecting data from.
            end_date (datetime.datetime, optional): Datetime to end collecting data from. Default is utcnow().
            timeframe (str): Timeframe identifier.

        Return:
            candles (list[alchemist_lib.database.ohlcv.Ohlcv]): List of ohlcv data.
            
        """
        
        assets = utils.to_list(assets)
        timeframe = timeframe.upper()
        availble_timeframes = [ds.available_timeframes for ds in self.session.query(PriceDataSource).join((Timeframe, PriceDataSource.available_timeframes)).filter(PriceDataSource.price_data_source_name == "poloniex").all()]
        assert timeframe not in availble_timeframes, "Timeframe not available for Poloniex."

        start = time.mktime(start_date.timetuple())
        end = time.mktime(end_date.timetuple())
        
        candles = []
        for asset in assets:
            try:
                chart_data = self.polo.returnChartData(currencyPair = "BTC_{}".format(asset.ticker),
                                                       period = utils.timeframe_to_seconds(timeframe = timeframe),
                                                       start = start,
                                                       end = end)
            except PoloniexError:
                continue

            for row in chart_data:
                candle = Ohlcv()

                if row["date"] == 0:
                    continue
                
                if timeframe == "1D":
                    candle.ohlcv_datetime = dt.datetime.fromtimestamp(row["date"]).strftime("%Y-%m-%d")
                else:
                    candle.ohlcv_datetime = dt.datetime.fromtimestamp(row["date"]).strftime("%Y-%m-%d %H:%M:%S")

                #logging.debug("OHLCV candle date: {}".format(candle.ohlcv_datetime))
                
                candle.timeframe_id = timeframe
                candle.open = Decimal(row["open"])
                candle.high = Decimal(row["high"])
                candle.low = Decimal(row["low"])
                candle.close = Decimal(row["close"])
                candle.volume = Decimal(row["volume"])
                candle.ticker = asset.ticker
                candle.instrument_id = asset.instrument_id

                candles.append(candle)

            time.sleep(PoloniexDataFeed.sleep_seconds)
            
        return candles
	
		
    
