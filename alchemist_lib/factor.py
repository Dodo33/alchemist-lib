import pandas as pd

import numpy as np

import pandas_talib

from sqlalchemy import desc

from decimal import Decimal

import datetime as dt

from . import datafeed

from . import utils

from .database.timeframe import Timeframe
from .database.ohlcv import Ohlcv

import logging

import warnings

warnings.filterwarnings("ignore")


def lin_reg(vals, index):
    # y = mx + q
    #https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.linalg.lstsq.html
    #x = index
    #y = vals

    A = np.vstack([index, np.ones(len(index))]).T
    
    m, q = np.linalg.lstsq(A, vals)[0]

    return Decimal(m)


class Factor():

    def __init__(self, session):
        self.session = session


    def history(self, universe, field, timeframe, window_length):
        field = field.lower()
        timeframe = timeframe.upper()
        available_timeframe = self.session.query(Timeframe).all()
        assert window_length > 0, "The window_length param must be > 0."
        assert field in ["open", "high", "low", "close", "volume", "*"], "Incorrect field. Supported: open, high, low, close, volume, *."
        assert timeframe not in available_timeframe, "Not supported timeframe."

        
        assets_to_update_ohlcv = datafeed.check_ohlcv_data(session = self.session, assets = universe, timeframe = timeframe, window_length = window_length)
        if len(assets_to_update_ohlcv) > 0:
            logging.debug("Assets OHLCV not updated: {}".format(assets_to_update_ohlcv))
            start = utils.get_last_date_checkpoint(timeframe = timeframe) - dt.timedelta(seconds = utils.timeframe_to_seconds(timeframe = timeframe) * window_length)
            datafeed.save_ohlcv(session = self.session, assets = assets_to_update_ohlcv, start_date = start, timeframe = timeframe)
        
        df = pd.DataFrame(columns = ["asset", "datetime", "open", "high", "low", "close", "volume"])
        for asset in universe:
            ohlcvs = self.session.query(Ohlcv).filter(Ohlcv.asset == asset,
                                                      Ohlcv.timeframe_id == timeframe).order_by(desc(Ohlcv.ohlcv_datetime)).limit(window_length).all()

            for row in ohlcvs:
                d = {"asset" : asset,
                     "datetime" : row.ohlcv_datetime,
                     "open" : row.open,
                     "high" : row.high,
                     "low" : row.low,
                     "close" : row.close,
                     "volume" : row.volume
                     }

                df = df.append(other = d, ignore_index = True)

        df.set_index(keys = ["asset", "datetime"], inplace = True)
        
        if field != "*":
            df = df[field]
            df = df.to_frame()

        if window_length == 1:
            df.index = df.index.droplevel(level = 1)
        
        return df

    
    def LinearRegression(self, values, window_length, field = None):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        #values must be a multi-index dataframe ( It was returned by history() ) and with a column called "value"
        val_df = values.copy()
        
        if field == None:
            field = list(val_df.columns)[0]
        
        main_df = pd.DataFrame(columns = ["asset", "LinearRegression"]).set_index(keys = ["asset"])
        for asset in val_df.index.levels[0]:
            df = val_df.loc[asset]
            df = df.sort_index(level = 0, ascending = False)
            df = df.head(window_length)

            vals = np.array([])
            index = np.array([])
            i = 0
            for price in df[field].tolist()[::-1]:
                vals = np.append(vals, float(price))
                index = np.append(index, i)
                i += 1

            main_df.loc[asset, "LinearRegression"] = lin_reg(vals = vals, index = index)

                         
        return main_df
    
    
    def MovingAverage(self, values, window_length, field = None):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        df = values.copy()
        
        if field == None:
            field = list(df.columns)[0]
        
        main_df = pd.DataFrame(columns = ["asset", "MovingAverage"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            vals = df.loc[asset]
            vals = vals.sort_index(level = 0, ascending = True)
            
            ma = pandas_talib.MA(df = vals, n = window_length, price = field)
            
            main_df.loc[asset, "MovingAverage"] = ma.tail(1)["MA_{}".format(window_length)].values[0]
            
        return main_df


    def SimpleMovingAverage(self, values, window_length, field = None):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        df = values.copy()
        
        if field == None:
            field = list(df.columns)[0]
        
        main_df = pd.DataFrame(columns = ["asset", "SimpleMovingAverage"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            vals = df.loc[asset]
            vals = vals.sort_index(level = 0, ascending = True)
            sma = pd.rolling_mean(arg = vals[field], window = window_length, min_periods = window_length).to_frame()
            main_df.loc[asset, "SimpleMovingAverage"] = sma.tail(1)["close"].values[0]
            
        return main_df
    

    def ExponentialMovingAverage(self, values, window_length, field = None):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        df = values.copy()
        
        if field == None:
            field = list(df.columns)[0]

        logging.debug(" ---------- ExponentialMovingAverage ---------- ")
        logging.debug("Field: {}".format(field))
        
        main_df = pd.DataFrame(columns = ["asset", "ExponentialMovingAverage"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            logging.debug(" --- {} --- ".format(asset.ticker))
            vals = df.loc[asset]
            vals = vals.sort_index(level = 0, ascending = True)
            logging.debug("vals: {}".format(vals))
            ema = pandas_talib.EMA(df = vals, n = window_length, price = field)
            logging.debug("ema: {}".format(ema))
            main_df.loc[asset, "ExponentialMovingAverage"] = ema.tail(1)["EMA_{}".format(window_length)].values[0]
            
        return main_df


    def Momentum(self, values, delta, field = None):
        assert delta > 0, "The delta param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        df = values.copy()
        
        if field == None:
            field = list(df.columns)[0]

        main_df = pd.DataFrame(columns = ["asset", "Momentum"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            vals = df.loc[asset]
            vals = vals.sort_index(level = 0, ascending = True)
            mom = pandas_talib.MOM(df = vals, n = delta, price = field)
            main_df.loc[asset, "Momentum"] = mom.tail(1)["Momentum_{}".format(delta)].values[0]
            
        return main_df


    def RateOfChange(self, values, window_length, field = None):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        assert len(list(values.columns)) > 0, "Values must have at least a column."
        df = values.copy()
        
        if field == None:
            field = list(df.columns)[0]

        main_df = pd.DataFrame(columns = ["asset", "RateOfChange"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            vals = df.loc[asset]
            vals = vals.sort_index(level = 0, ascending = True)
            roc = pandas_talib.ROC(df = vals, n = window_length, price = field)
            main_df.loc[asset, "RateOfChange"] = roc.tail(1)["ROC_{}".format(window_length)].values[0]
            
        return main_df
    

    def AverageTrueRange(self, values, window_length):
        assert window_length > 0, "The window_length param must be > 0."
        values = utils.to_frame(values)
        df = values.copy()

        main_df = pd.DataFrame(columns = ["asset", "AverageTrueRange"]).set_index(keys = ["asset"])
        for asset in df.index.levels[0]:
            asset_df = df.loc[asset]
            asset_df["asset"] = asset
            
            asset_df.reset_index(inplace = True)
            asset_df.set_index(keys = ["asset", "datetime"], inplace = True)
            
            #https://stackoverflow.com/questions/35753914/calculating-average-true-range-column-in-pandas-dataframe
            asset_df["ATR1"] = abs(asset_df["high"] - asset_df["low"])
            asset_df["ATR2"] = abs(asset_df["high"] - asset_df["close"].shift())
            asset_df["ATR3"] = abs(asset_df["low"] - asset_df["close"].shift())
            asset_df["ATR"] = asset_df[["ATR1", "ATR2", "ATR3"]].max(axis = 1)
            
            emaAtr = self.ExponentialMovingAverage(values = asset_df, window_length = window_length, field = "ATR")
            main_df.loc[asset, "AverageTrueRange"] = emaAtr.tail(1)["ExponentialMovingAverage"].values[0]
        
        return main_df
		
		
		
        
    
