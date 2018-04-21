import numpy as np

import pandas as pd

import datetime as dt

import pytz



#https://stackoverflow.com/questions/998938/handle-either-a-list-or-single-integer-as-an-argument
def to_list(item):
    l = item
    if not isinstance(item, list):
        if isinstance(item, np.ndarray):
            l = item.tolist()
        else:
            l = [ item ]
    return l


def subtract_list(first, second):
    new_list = []
    
    if isinstance(first, list) == False or isinstance(second, list) == False:
        return []
    
    for item in first:
        if item not in second:
            new_list.append(item)
            
    return new_list


def to_frame(serie):
    if isinstance(serie, pd.Series):
        serie = serie.to_frame()
    return serie


#https://stackoverflow.com/questions/12851791/removing-numbers-from-string
def get_timeframe_data(timeframe):
    tf_unit = ''.join([i for i in timeframe if not i.isdigit()])
    tf = int(''.join([i for i in timeframe if i.isdigit()]))

    return tf, tf_unit


def timeframe_to_seconds(timeframe):
    timeframe = timeframe.upper()
    
    unit_to_seconds = {"D" : 60 * 60 * 24,
                       "H" : 60 * 60,
                       "M" : 60
                       }
    
    tf, unit = get_timeframe_data(timeframe = timeframe)
    return tf * unit_to_seconds[unit]
    

def get_data_source_names_from_asset(asset):
    names = []
    for exch in asset.exchanges:
        names.append(exch.price_data_source.price_data_source_name)
    return names


def get_last_date_checkpoint(timeframe):
    tf, tf_unit = get_timeframe_data(timeframe = timeframe)
    
    now = dt.datetime.utcnow()

    while True:
        if tf_unit == "M":
            if now.minute % tf == 0:
                now = now.replace(second = 0, microsecond = 0)
                break
        if tf_unit == "H":
            if now.hour % tf == 0:
                now = now.replace(minute = 0, second = 0, microsecond = 0)
                break
        if tf_unit == "D":
            if now.day % tf == 0:
                now = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
                break
        now = now - dt.timedelta(minutes = 1)
        
    return now


def execution_time_str(timetable, delay):
    assert isinstance(delay, str), "Delay must be a string."
    delay = delay.upper()
    assert len(delay) > 0, "Length of delay must be > 0"
    assert delay[-1] in ["M", "H"], "Delay must be a string as [NUMBER][TIMEUNIT]. For example: 15M"
        
    tf, tf_unit = get_timeframe_data(timeframe = delay)

    job_params = {}
    
    if timetable == None:
        job_params["trigger"] = "cron"
        if tf_unit == "M":
            if tf > 30:
                raise NotImplemented
            else:
                job_params["minute"] = "0-59/{}".format(tf)
        elif tf_unit == "H":
            if tf > 12:
                raise NotImplemented
            else:
                job_params["hour"] = "0-23/{}".format(tf)
        job_params["timezone"] = pytz.utc
    else:
        today = dt.datetime.utcnow()
        
        job_params["trigger"] = "interval"

        if tf_unit == "M":
            job_params["minutes"] = tf
        elif tf_unit == "H":
            job_params["hours"] = tf
        
        job_params["start_date"] = today.replace(hour = timetable.open_hour, minute = timetable.open_minute, second = 0).strftime("%Y-%m-%d %H:%M:%S")
        job_params["end_date"] = today.replace(hour = timetable.close_hour, minute = timetable.close_minute, second = 0).strftime("%Y-%m-%d %H:%M:%S")
        job_params["timezone"] = timetable.timezone
    
    return job_params
    

def print_list(l):
    if isinstance(l, list) == False:
        return l

    s = "\n"
    for item in l:
        s += (str(item) + "\n")

    return s



def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")










    

