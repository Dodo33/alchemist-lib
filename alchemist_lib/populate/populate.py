from abc import ABC, abstractmethod



class PopulateBaseClass(ABC):

    """
    Abstract class for every populate class.

    Abstract methods:
        - get_exchange_instance(): Save all data associated with an exchange and returns an instance of alchemist_lib.database.exchange.Exchange.
        - populate(): Save all assets traded in a specific exchange.
        - update_asset_list(): Update the list of assets tradable in an exchange, remove delisted assets and add new assets.

    Attributes:
        saver (alchemist_lib.populate.saver.Saver): Instance of the saver class.
    """

    def __init__(self, saver):
        self.saver = saver


    @abstractmethod
    def get_exchange_instance(self):
        pass


    @abstractmethod
    def populate(self):
        pass
    

    @abstractmethod
    def update_asset_list(self):
        pass
