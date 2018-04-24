from abc import ABC, abstractmethod

from decimal import Decimal

from ..database.ptf_allocation import PtfAllocation
from ..database.instrument import Instrument

from .. import utils

from .. import datafeed



class PortfolioBaseClass(ABC):

    """
    Abstract class used by modules that manage the portfolio costructor.

    Abstract methods:
        - normalize_weights(df): It has to return a dataframe (pandas.DataFrame) with the following columns:
            * asset (alchemist_lib.database.asset.Asset): Must be the index.
            * weight (decimal.Decimal): The weight of the specified asset in the portfolio. The sum of all weights in the dataframe must be near 100 (or 1).
        - set_allocation(session, name, df): It has to return a list of allocations (alchemist_lib.database.ptf_allocation.PtfAllocation) based on the type of portfolio you want.
        
    Attributes:
        capital (decimal.Decimal): Capital allocated for the portfolio.
    """

    def __init__(self, capital):

        """
        Costructor method.

        Args:
            capital (int, float, str, decimal.Decimal): Capital allocated for the portfolio.
        """
        
        self.capital = Decimal(capital)


    @abstractmethod
    def set_allocation(self, session, name, df):
        pass


    def rebalance(self, curr_ptf, target_ptf):

        """
        This method returns a list of PtfAllocation (alchemist_lib.database.ptf_allocation.PtfAllocation) that will be executed in order to mantain the portfolio rebalanced.

        Args:
            curr_ptf (alchemist_lib.database.ptf_allocation.PtfAllocation, list[PtfAllocation]): Current portfolio, loaded from the database.
            target_ptf (alchemist_lib.database.ptf_allocation.PtfAllocation, list[PtfAllocation]): Ideal portfolio.

        Return:
            new_ptf (list[alchemist_lib.database.ptf_allocation.PtfAllocation]): List of PtfAllocation to execute in order to get the ideal portfolio.

        """

        curr_ptf = utils.to_list(curr_ptf)
        target_ptf = utils.to_list(target_ptf)
        
        new_ptf = []
        found = False
        
        for new_alloc in target_ptf:
            found = False
            for old_alloc in curr_ptf:
                if new_alloc.asset == old_alloc.asset:
                    allocation = PtfAllocation(amount = new_alloc.amount - old_alloc.amount,
                                               base_currency_amount = new_alloc.base_currency_amount - old_alloc.base_currency_amount,
                                               ticker = new_alloc.ticker,
                                               instrument_id = new_alloc.instrument_id,
                                               ts_name = new_alloc.ts_name)
                    allocation.asset = new_alloc.asset
                    allocation.ts = new_alloc.ts
                    new_ptf.append(allocation)
                    found = True
            if found == False:
                allocation = new_alloc.deepcopy()
                """PtfAllocation(amount = new_alloc.amount,
                                           base_currency_amount = new_alloc.base_currency_amount,
                                           ticker = new_alloc.ticker,
                                           instrument_id = new_alloc.instrument_id,
                                           ts_name = new_alloc.ts_name)
                """
                allocation.asset = new_alloc.asset
                allocation.ts = new_alloc.ts
                new_ptf.append(allocation)
        
        for old_alloc in curr_ptf:
            found = False
            for new_alloc in target_ptf:
                if old_alloc.asset == new_alloc.asset:
                    found = True
            if found == False:
                allocation = PtfAllocation(amount = old_alloc.amount * Decimal(-1),
                                           base_currency_amount = old_alloc.base_currency_amount * Decimal(-1),
                                           ticker = old_alloc.ticker,
                                           instrument_id = old_alloc.instrument_id,
                                           ts_name = old_alloc.ts_name)
                allocation.asset = old_alloc.asset
                allocation.ts = old_alloc.ts
                new_ptf.append(allocation)

        return new_ptf


    def load_ptf(self, session, name):

        """
        Load the current portfolio from the database. After that, It updates the base_currency_amount attribute.

        Args:
            session (sqlalchemy.orm.session.Session): Database connection.
            name (str): Name of the trading system which manages the portfolio.

        Return:
            allocs (list[PtfAllocation]): List of allocations of the specified trading system.
        """
        
        allocs = session.query(PtfAllocation).filter(PtfAllocation.ts_name == name).all()
        assets = [alloc.asset for alloc in allocs]

        last_price = datafeed.get_last_price(assets = assets)
        
        for alloc in allocs:
            alloc.base_currency_amount = alloc.amount * last_price.loc[alloc.asset, "last_price"]
        
        return allocs
        
                




















    
    
    
