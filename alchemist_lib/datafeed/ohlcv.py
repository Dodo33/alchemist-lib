from abc import ABC, abstractmethod
import datetime as dt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from .. import utils

import logging



class OhlcvBaseClass(ABC):

    """
    Abstract class used by modules that manage OHLCV data.

    Abstract methods:
        - get_last_price(assets): It has to return a dataframe (pandas.DataFrame) with the following columns:
            * asset (alchemist_lib.database.asset.Asset): Must be the index.
            * last_price (decimal.Decimal): The last trade price of the asset.
        - get_ohlcv(assets, start_date, end_date, timeframe): It has to return a list of Ohlcv (alchemist_lib.database.ohlcv.Ohlcv).

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
    """

    def __init__(self, session):

        """
        Costructor method.

        Args:
            session (sqlalchemy.orm.session.Session): Connection to the database.
        """
        
        self.session = session
        
        
    @abstractmethod
    def get_last_price(self, assets):
        pass

    
    @abstractmethod
    def get_ohlcv(self, assets, start_date, timeframe, end_date = dt.datetime.utcnow()):
        pass


    def _save(self, data):
        
        """
        Save records in the database.
        
        This method doesn't use ``self.session.add_all(data)`` because some objects
        could raise sqlalchemy.exc.IntegrityError and so nothing will be saved.
        Save an object per time allow us to pass away IntegrityError.

        Args:
            data (list[obj]): List of map class instances.

        """
        
        for obj in data:
            try:
                self.session.add(obj)
                self.session.commit()
            except (IntegrityError, FlushError) as e:
                self.session.rollback()
                #logging.debug("An object can't be saved. Obj: {}. Exception: {}".format(obj, e))
                

    def save_ohlcv(self, assets, start_date, timeframe, end_date = dt.datetime.utcnow()):

        """
        This method collects and saves OHLCV data from the data source.

        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
            start_date (datetime.datetime): Datetime to start collecting data from.
            end_date (datetime.datetime, optional): Datetime to end collecting data from. Default is utcnow().
            timeframe (str): Timeframe identifier.
        """
        
        candles = self.get_ohlcv(assets = assets, start_date = start_date, end_date = end_date, timeframe = timeframe)
        self._save(data = candles)


    def get_last_ohlcv(self, assets, timeframe):

        """
        This method collects the last OHLCV candle.

        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
            timeframe (str): Timeframe identifier.

        Return:
            candles (list[alchemist_lib.database.ohlcv.Ohlcv]): List of candles. 
        """
        
        candles = []
        for asset in assets:
            now = dt.datetime.utcnow()
            
            if asset.instrument.instrument_type == "cryptocurrency":
                delta = dt.timedelta(seconds = utils.timeframe_to_seconds(timeframe = timeframe))
                past = now - delta

                candles += self.get_ohlcv(assets = asset, start_date = past, end_date = now, timeframe = timeframe)
                
            else:
                logging.critical("The instrument is not a cryptocurrency. NotImplemented raised.")
                raise NotImplemented
                
        return candles

        
    def save_last_ohlcv(self, assets, timeframe):

        """
        This method collects and saves the last OHLCV candle.

        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
            timeframe (str): Timeframe identifier.
        """
        
        candles = self.get_last_ohlcv(assets = assets, timeframe = timeframe)
        self._save(data = candles)










        

