import datetime as dt

import pandas as pd

from .poloniexdatafeed import PoloniexDataFeed
from .bittrexdatafeed import BittrexDataFeed

from ..database.ohlcv import Ohlcv

from .. import utils



def get_data_sources_dict(session):

    """
    Remember to change this method every time you add a module.

    Args:
        session (sqlalchemy.orm.session.Session): Connection to the database.

    Return:
        dsd (dict): Return a dictionary. The key must be the name of the data source in the database and the value must be an instance of the module charged to collect data.
    """
    
    dsd = {"poloniex" : PoloniexDataFeed(session = session),
            "bittrex" : BittrexDataFeed(session = session)
           }
    
    return dsd


def get_last_price(assets):

    """
    Returns the last trade price for every asset.
    The last price is retrived based on ``alchemist_lib.datafeed.get_data_sources_dict()``.

    Args:
        assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want last trade price of.

    Return:
        df (pandas.DataFrame): A dataframe with the following columns:
            * asset (alchemist_lib.database.asset.Asset): Must be the index.
            * last_price (decimal.Decimal): The last price of the associated asset. 
    """

    assets = utils.to_list(assets)
    data_feed_source = None
    ds = get_data_sources_dict(session = None)
    
    df = pd.DataFrame(columns = ["asset", "last_price"]).set_index("asset")
    for asset in assets:
        data_source_names = utils.get_data_source_names_from_asset(asset = asset)

        for ds_name, ds_inst in ds.items():
            if ds_name in data_source_names:
                data_feed_source = ds_inst
                break

        try:
            lp = data_feed_source.get_last_price(assets = asset)
        except AttributeError:#If data_feed_source remains None
            lp = pd.DataFrame()
            
        df = pd.concat([df, lp])

    return df


def save_ohlcv(session, assets, start_date, timeframe):

    """
    This method collects and saves OHLCV data ( from start_date to utcnow() ).

    Args:
        session (sqlalchemy.orm.session.Session): Database connection.
        assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
        start_date (datetime.datetime): Datetime to start collecting data from.
        timeframe (str): Timeframe identifier.
    """

    assets = utils.to_list(assets)
    ds = get_data_sources_dict(session = session)
    exch_assets = {}
    
    for asset in assets:
        data_source_names = utils.get_data_source_names_from_asset(asset = asset)

        for ds_name, ds_inst in ds.items():
            if ds_name in data_source_names:
                exch_assets.setdefault(ds_name, []).append(asset)


    for ds_name, ds_inst in ds.items():
        try:
            ds_inst.save_ohlcv(assets = exch_assets[ds_name], start_date = start_date, timeframe = timeframe)
        except Exception:
            pass

    
def save_last_ohlcv(session, assets, timeframe):

    """
    This method collects and saves the last OHLCV candle.

    Args:
        assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
        timeframe (str): Timeframe identifier.
    """

    assets = utils.to_list(assets)
    ds = get_data_sources_dict(session = session)
    exch_assets = {}
    
    for asset in assets:
        data_source_names = utils.get_data_source_names_from_asset(asset = asset)

        for ds_name, ds_inst in ds.items():
            if ds_name in data_source_names:
                exch_assets.setdefault(ds_name, []).append(asset)

    for ds_name, ds_inst in ds.items():
        try:
            ds_inst.save_last_ohlcv(assets = exch_assets[ds_name], timeframe = timeframe)
        except Exception:
            pass


def check_ohlcv_data(session, assets, timeframe, window_length):

    """
    Check if all OHLCV candles needed are already saved in the db.
    It's useful in order to not requests OHLCV data more times (in different functions).

    Args:
        session (sqlalchemy.orm.session.Session): Database connection.
        assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets which we want informations of.
        timeframe (str): Timeframe identifier.
        window_length (int): The number of steps to do in the past.

    Return:
        assets_toret (list[Asset]): List of not-updated assets.
    """
    
    assets_toret = []
    tf, tf_unit = utils.get_timeframe_data(timeframe = timeframe)
    start_date = utils.get_last_date_checkpoint(timeframe = timeframe)

    for asset in assets:
        for i in range(window_length):
            step = start_date - dt.timedelta(seconds = utils.timeframe_to_seconds(timeframe = timeframe) * i)
            
            res = session.query(Ohlcv).filter(Ohlcv.ohlcv_datetime == step,
                                              Ohlcv.asset == asset,
                                              Ohlcv.timeframe_id == timeframe).all()
            
            if len(res) <= 0:
                assets_toret.append(asset)
                break

    return assets_toret
    












        



    
