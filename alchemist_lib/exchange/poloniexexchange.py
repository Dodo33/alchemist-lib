from poloniex import Poloniex

from .exchange import ExchangeBaseClass

from .. import utils

from decimal import Decimal

import logging



class PoloniexExchange(ExchangeBaseClass):

    """
    Class that manages Poloniex metadata.
    Inherits from alchemist_lib.exchange.exchange.ExchangeBaseClass.
    
    Website: https://poloniex.com/

    Api documentation: https://poloniex.com/support/api/

    Api wrapper: https://github.com/s4w3d0ff/python-poloniex

    Attributes:
        polo (poloniex.Poloniex): Communication object.
    
    """

    def __init__(self):

        """
        Costructor method.
        """
        
        ExchangeBaseClass.__init__(self)
        self.polo = Poloniex()


    def get_min_order_size(self, asset):

        """
        This method would return the minimum order size for a specific market, but It's not specified in the Poloniex documentation.
        https://poloniex.com/support/api/

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset traded again BTC.
            
        Return:
            size (decimal.Decimal): Minimum order size. Default is 0.
        """
        
        return Decimal(0)
    

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
        
        pairs = self.polo.returnTicker()
        
        tradable = []
        for asset in assets:
            pair = "BTC_{}".format(asset.ticker)
            if pair in list(pairs.keys()):
                if pairs[pair]["isFrozen"] == "0":
                    tradable.append(asset)
                else:
                    logging.debug("{} is not tradable.".format(asset.ticker))
        
        return tradable

		
