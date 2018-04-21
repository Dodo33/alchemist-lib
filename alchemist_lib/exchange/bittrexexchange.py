from bittrex.bittrex import Bittrex

from .exchange import ExchangeBaseClass

from .. import utils

from decimal import Decimal

import logging



class BittrexExchange(ExchangeBaseClass):

    """
    Class that manages Bittrex metadata.
    Inherits from alchemist_lib.exchange.exchange.ExchangeBaseClass.
    
    Website: https://bittrex.com/

    Api documentation: https://bittrex.com/Home/Api

    Api wrapper: https://github.com/ericsomdahl/python-bittrex

    Attributes:
        bittrex (bittrex.bittrex.Bittrex): Communication object.
    
    """

    def __init__(self):

        """
        Costructor method.
        """
        
        ExchangeBaseClass.__init__(self)
        self.bittrex = Bittrex(api_key = None, api_secret = None)


    def are_tradable(self, assets):
    
        """
        Filters tradable assets.
        
        Args:
            assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets to check.
                
        Return:
            tradable (list[Asset]): Returns all tradable asset (remove not tradable assets from the arg).
                
        Note:
            Checks just pairs with BTC as base currency.
        """
        
        assets = utils.to_list(assets)
        
        markets = self.bittrex.get_markets()

        if markets["result"] == None:
            logging.warning("Bittrex api result is None. are_tradable() method.")
            return assets

        markets = markets["result"]

        markets_name = [m["MarketName"] for m in markets]
        
        tradable = []
        for asset in assets:
            pair = "BTC-{}".format(asset.ticker)
            if pair in markets_name:
                for m in markets:
                    if m["MarketName"] == pair:
                        if m["IsActive"] == True:
                            tradable.append(asset)
                        else:
                            logging.debug("{} is not tradable.".format(asset.ticker))
        
        return tradable

	
    def get_min_order_size(self, asset):

        """
        This method returns the minimum order size for a specific market.

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset traded again BTC.
            
        Return:
            size (decimal.Decimal): Minimum order size. Default is 0.
        """

        pair = "BTC-{}".format(asset.ticker)
        markets = self.bittrex.get_markets()
            
        if markets["result"] == None or markets["success"] == False:
            logging.warning("Bittrex api result is None or success is False. get_min_trade_size() method.")
            return Decimal(0)
            
        markets = markets["result"]
            
        for market in markets:
            if market["MarketName"] == pair:
                return Decimal(market["MinTradeSize"])
            
        return Decimal(0)
