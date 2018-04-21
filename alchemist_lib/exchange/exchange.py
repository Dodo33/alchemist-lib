from abc import ABC, abstractmethod



class ExchangeBaseClass(ABC):

    """
    Abstract class for every exchange module.

    Abstract methods:
        - are_tradable(assets): It has to filter the args and returns just assets that are tradable.
        - get_min_trade_size(asset): It has to returns the minimum order size based on the specified market.
    """

    def __init__(self):

        """
        Costructor method. (no attributes, no args)
        """
        
        pass


    @abstractmethod
    def are_tradable(self, assets):
        pass
	
	
    @abstractmethod
    def get_min_order_size(self, asset):
        pass
