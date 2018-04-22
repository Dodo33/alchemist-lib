from bittrex.bittrex import Bittrex, API_V2_0, API_V1_1

import pandas as pd

import urllib.request as req

import json

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



class BittrexDataFeed(OhlcvBaseClass):

    """
    Class that collects data from Bittrex.
    Inherits from alchemist_lib.datafeed.ohlcv.OhlcvBaseClass.

    Website: https://bittrex.com/

    Api documentation: https://bittrex.com/Home/Api

    Api wrapper: https://github.com/ericsomdahl/python-bittrex

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
        bittrex (bittrex.bittrex.Bittrex): Communication object.
    """

    sleep_seconds = 0.4
    available_timeframe = {"1M" : "oneMin",
                           "5M" : "fiveMin",
                           "30M" : "thirtyMin",
                           "1H" : "hour",
                           "1D" : "day"
                           }
    
    def __init__(self, session):

        """
        Costructor method.

        Args:
            session (sqlalchemy.orm.session.Session): Connection to the database.
        """
        
        OhlcvBaseClass.__init__(self, session = session)
        self.bittrex = Bittrex(api_key = "APIKEY", api_secret = "SECRETKEY", api_version = API_V1_1)
        self.bittrex2 = Bittrex(api_key = "APIKEY", api_secret = "SECRETKEY", api_version = API_V2_0)


    def get_assets(self):

        """
        Returns the list of traded asset.

        Return:
            assets (list[alchemist_lib.database.asset.Asset]): List of assets.

        Note:
            Returns only pairs with bitcoin as base currency.
        """
        
        markets = self.bittrex.get_markets()
        if markets["result"] == None:
            logging.warning("Bittrex api result is None. get_assets() method.")
            return []
        
        cryptocurrency_id = self.session.query(Instrument.instrument_id).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
        
        assets = []
        for market in markets["result"]:
            if market["BaseCurrency"] == "BTC":
                asset = Asset(ticker = market["MarketCurrency"], instrument_id = cryptocurrency_id, name = market["MarketCurrencyLong"])
                assets.append(asset)
                
        return assets
        

    def get_last_price(self, assets):

        """
        Retrieves last trade price for every asset in the list.

        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want the last trade price of.

        Return:
            df (pandas.DataFrame): A dataframe with the following columns:
                * asset (alchemist_lib.database.asset.Asset): Must be the index.
                * last_price (decimal.Decimal): The last price of the associated asset.
            If some prices are not retrieved the last_price attribute will be 0.
        """
        
        assets = utils.to_list(assets)
        
        market_summaries = self.bittrex2.get_market_summaries()

        while(True):
            if market_summaries["result"] == None or market_summaries["success"] == False:
                logging.warning("Bittrex api result is None or success is False. get_last_price() method.")
                time.sleep(60)
                
                #return pd.DataFrame(data = {"asset" : assets, "last_price" : Decimal(0)}, columns = ["asset", "last_price"]).set_index("asset")
            else:
                break
                
        market_summaries = market_summaries["result"]
        
        df = pd.DataFrame(data = {"asset" : assets}, columns = ["asset", "last_price"]).set_index("asset")
        for asset in assets:
            pair = "BTC-{}".format(asset.ticker)

            found = False
            for market in market_summaries:
                if market["Summary"]["MarketName"] == pair:
                    df.loc[asset, "last_price"] = Decimal(market["Summary"]["Last"])
                    found = True

            if found == False:
                logging.debug("{} market not found. last_price will be 0.".format(pair))
                df.loc[asset, "last_price"] = Decimal(0)
            else:        
                logging.debug("{} last price: {}".format(asset.ticker, df.loc[asset, "last_price"]))

        return df
    
        
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
        availble_timeframes = [ds.available_timeframes for ds in self.session.query(PriceDataSource).join((Timeframe, PriceDataSource.available_timeframes)).filter(PriceDataSource.price_data_source_name == "bittrex").all()]
        assert timeframe not in availble_timeframes, "Timeframe not available for BittrexDataFeed."

        end_point = "https://bittrex.com/Api/v2.0/pub/market/GetTicks"

        candles = []
        for asset in assets:
            url = end_point + "?marketName=BTC-{}&tickInterval={}".format(asset.ticker, BittrexDataFeed.available_timeframe[timeframe])
            
            json_data = req.urlopen(url)
            data = json.loads(json_data.read().decode("UTF-8"))
            results = data["result"]

            if results == None:
                logging.warning("Bittrex api result is None. get_ohlcv() method. Asset: {}".format(asset.ticker))
                continue
            
            results = [item for item in results if dt.datetime.strptime(item["T"], '%Y-%m-%dT%H:%M:%S') < end_date and dt.datetime.strptime(item["T"], '%Y-%m-%dT%H:%M:%S') > start_date]

            for row in results:
                candle = Ohlcv()
                
                candle.ohlcv_datetime = dt.datetime.strptime(row["T"], '%Y-%m-%dT%H:%M:%S')
                candle.timeframe_id = timeframe
                candle.open = Decimal(row["O"])
                candle.high = Decimal(row["H"])
                candle.low = Decimal(row["L"])
                candle.close = Decimal(row["C"])
                candle.volume = Decimal(row["V"])
                candle.ticker = asset.ticker
                candle.instrument_id = asset.instrument_id

                candles.append(candle)

            time.sleep(BittrexDataFeed.sleep_seconds)
            
        return candles
		
