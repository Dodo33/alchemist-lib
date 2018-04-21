from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from .. import utils

from ..database.instrument import Instrument
from ..database.timeframe import Timeframe
from ..database.broker import Broker
from ..database.price_data_source import PriceDataSource
from ..database.exchange import Exchange
from ..database.asset import Asset
from ..database.timetable import Timetable



class Saver():

    """
    Class that saves data on the database.

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
    """
    
    def __init__(self, session):

        """
        Costructor method.

        Args:
            session (sqlalchemy.orm.session.Session): Database connection.
        """
        
        self.session = session


    def _save(self, obj):

        """
        Save an instance of a map class.

        Args:
            obj (obj): Instance to save.
        """
        
        try:
            self.session.add(obj)
            self.session.commit()
        except (IntegrityError, FlushError):
            self.session.rollback()


    def instrument(self, kind):

        """
        Save an instrument on the db.

        Args:
            kind (str): Kind of instrument to save. (instrument_type)

        Return:
            instrument (alchemist_lib.database.instrument.Instrument): Map class instance.
        """
        
        already_saved = self.session.query(Instrument).filter(Instrument.instrument_type == kind).all()
        if len(already_saved) > 0:
            return already_saved[0]

        instrument = Instrument(instrument_type = kind)
        self._save(instrument)
        return instrument


    def timeframe(self, id, description):

        """
        Save a timeframe on the db.

        Args:
            if (str): Timeframe identifier. (15M as example).
            description (str): The definition of the timeframe in english words. (fifteen minutes as example).

        Return:
            tf (alchemist_lib.database.timeframe.Timeframe): Map class instance.
        """
        
        tf = Timeframe(timeframe_id = id, description = description)
        self._save(tf)
        return tf
    

    def broker(self, name, site):

        """
        Save a broker on the db.

        Args:
            name (str): Name of the broker.
            site (str): Website of the broker.

        Return:
            broker (alchemist_lib.database.broker.Broker): Map class instance.
        """
        
        broker = Broker(broker_name = name, website = site)
        self._save(broker)
        return broker


    def data_source(self, name, site, timeframes):

        """
        Save a data_source on the db.

        Args:
            name (str): Name of the data source.
            site (str): Website of the data source.
            timeframes (list[alchemist_lib.database.timeframe.Timeframe]): List of supported timeframes.

        Return:
            ds (alchemist_lib.database.price_data_source.PriceDataSource): Map class instance.
        """
        
        timeframes = utils.to_list(timeframes)

        tfs = self.session.query(Timeframe).filter(Timeframe.timeframe_id.in_([t.timeframe_id for t in timeframes])).all()
        
        ds = PriceDataSource(price_data_source_name = name, website = site)
        ds.available_timeframes = tfs
        self._save(ds)            
        return ds


    def timetable(self, open_hour, open_minute, close_hour, close_minute, timezone):

        """
        Save a timetable on the db.

        Args:
            open_hour (int): Hour the market opens.
            open_minute (int): Minute the market opens.
            close_hour (int): Hour the market closes.
            close_minute (int): Minute the market closes.
            timezone (str): Timezone name.

        Return:
            tt (alchemist_lib.database.timetable.Timetable): Map class instance.
        """
        
        tt = Timetable(open_hour = open_hour,
                       open_minute = open_minute,
                       close_hour = close_hour,
                       close_minute = close_minute,
                       timezone = timezone)
        self._save(tt)
        return tt
    

    def exchange(self, name, website, data_source, timetable, brokers):
        
        """
        Save an exchange on the db.

        Args:
            name (str): Name of the exchange.
            website (str): Website of the exchange.
            data_source (alchemist_lib.database.price_data_source.PriceDataSource): PriceDataSource instance associated with this exchange. Specify how to get price informations.
            timetable (alchemist_lib.database.timetable.Timetable): Timetable of this exchange.
            brokers (list[alchemist_lib.database.broker.Broker]): Brokers that allow trading on this exchange.

        Return:
            exchange (alchemist_lib.database.exchange.Exchange): Map class instance.
        """
        
        brokers = utils.to_list(brokers)

        if data_source != None:
            ds = self.session.query(PriceDataSource).filter(PriceDataSource.price_data_source_name == data_source.price_data_source_name).one()
        else:
            ds = data_source
            
        if timetable != None:
            tt = self.session.query(Timetable).filter(Timetable.open_hour == timetable.open_hour,
                                                      Timetable.open_minute == timetable.open_minute,
                                                      Timetable.close_hour == timetable.close_hour,
                                                      Timetable.close_minute == timetable.close_minute,
                                                      Timetable.timezone == timetable.timezone).one()
        else:
            tt = timetable
        
        brks = self.session.query(Broker).filter(Broker.broker_name.in_([b.broker_name for b in brokers])).all()
        
        exchange = Exchange(exchange_name = name, website = website)
        exchange.price_data_source = ds
        exchange.timetable = tt
        exchange.brokers = brks
        self._save(exchange)
        return exchange


    def asset(self, ticker, instrument_id, name, exchanges):

        """
        Save an asset on the db.

        Args:
            ticker (str): Ticker code of the asset.
            instrument_id (int): Financial instrument identifier.
            name (str): Long name of the asset.
            exchanges (list[alchemist_lib.database.asset.Asset]): Exchanges where this asset is tradable.

        Return:
            tt (alchemist_lib.database.asset.Asset): Map class instance.
        """
        
        exchanges = utils.to_list(exchanges)

        exchanges_already_saved = self.session.query(Exchange).join(Exchange, Asset.exchanges).filter(Asset.ticker == ticker, Asset.instrument_id == instrument_id).all()
        exchs = self.session.query(Exchange).filter(Exchange.exchange_name.in_([e.exchange_name for e in exchanges])).all()

        asset = Asset(ticker = ticker, instrument_id = instrument_id, name = name)
        asset.exchanges = exchanges_already_saved + exchs

        obj = asset
        try:
            self.session.add(obj)
            self.session.commit()
        except (IntegrityError, FlushError):
            self.session.rollback()
            
            asset = self.session.query(Asset).filter(Asset.ticker == obj.ticker).one()
            asset.exchanges = exchanges_already_saved + exchs
            try:
                self.session.add(asset)
                self.session.commit()
            except (IntegrityError, FlushError):
                self.session.rollback()
            
        return asset
        
















        
    

        
