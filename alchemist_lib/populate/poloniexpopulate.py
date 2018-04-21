from .populate import PopulateBaseClass

from ..datafeed import PoloniexDataFeed

from ..database.asset import Asset
from ..database.instrument import Instrument
from ..database.exchange import Exchange

from .. import utils



class PoloniexPopulate(PopulateBaseClass):

    """
    Class that manages the population of the database with data from Poloniex.
    Inherits from alchemist_lib.populate.populate.PopulateBaseClass.

    Attributes:
        saver (alchemist_lib.populate.saver.Saver): Saver class instance.
    """
    
    def __init__(self, saver):

        """
        Costructor method.

        Args:
            saver (alchemist_lib.populate.saver.Saver): Saver class instance.
        """
        
        PopulateBaseClass.__init__(self, saver = saver)

    
    def get_exchange_instance(self):

        """
        Save all informations about Poloniex and returns an Exchange instance.

        Return:
            exchange (alchemist_lib.database.exchange.Exchange): Exchange instance.
        """
        
        instrument = self.saver.instrument(kind = "cryptocurrency")
        m15 = self.saver.timeframe(id = "15M", description = "five minutes")
        m30 = self.saver.timeframe(id = "30M", description = "thirty minutes")
        h2 = self.saver.timeframe(id = "2H", description = "two hours")
        h4 = self.saver.timeframe(id = "4H", description = "four hours")
        d1 = self.saver.timeframe(id = "1D", description = "one day")
        broker = self.saver.broker(name = "poloniex", site = "www.poloniex.com")
        datasource = self.saver.data_source(name = "poloniex", site = "www.poloniex.com", timeframes = [m15, m30, h2, h4, d1])
        timetable = None
        exchange = self.saver.exchange(name = "poloniex", website = "www.poloniex.com", data_source = datasource, timetable = timetable, brokers = [broker])
            
        return exchange


    def populate(self):

        """
        Populate the database with all tradable assets on Poloniex.
        """
         
        exchange = self.get_exchange_instance()
            
        assets = PoloniexDataFeed(session = self.saver.session).get_assets()
        
        for asset in assets:
            self.saver.asset(ticker = asset.ticker, instrument_id = asset.instrument_id, name = asset.name, exchanges = exchange)

        cryptocurrency_id = self.saver.session.query(Instrument).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
        self.saver.asset(ticker = "BTC", instrument_id = cryptocurrency_id, name = "Bitcoin", exchanges = exchange)
        
		
    def update_asset_list(self):

        """
        Update the list of assets traded on Poloniex.
        """
        
        db_assets = self.saver.session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == "poloniex").all()
        poloniex_assets = PoloniexDataFeed(session = self.saver.session).get_assets()

        cryptocurrency_id = self.saver.session.query(Instrument).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
        poloniex_assets.append(Asset(ticker = "BTC", instrument_id = cryptocurrency_id, name = "Bitcoin"))
            
        assets_to_save = utils.subtract_list(first = poloniex_assets, second = db_assets)
        assets_to_remove = utils.subtract_list(first = db_assets, second = poloniex_assets)

        for asset in assets_to_save:
            exchange = self.get_exchange_instance()
            self.saver.asset(ticker = asset.ticker, instrument_id = asset.instrument_id, name = asset.name, exchanges = [exchange])

        for asset in assets_to_remove:
            self.saver.session.delete(asset)
            self.saver.session.commit()
	
