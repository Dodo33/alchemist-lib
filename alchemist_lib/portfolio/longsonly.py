import numpy as np
from decimal import Decimal, DivisionByZero

from ..database.ptf_allocation import PtfAllocation

from .portfolio import PortfolioBaseClass

from .. import datafeed



class LongsOnlyPortfolio(PortfolioBaseClass):
    
    """
    Class that manages the creation of a portfolio of longs-only positions.
    Inherits from alchemist_lib.portfolio.portfolio.PortfolioBaseClass.

    Attributes:
        capital (decimal.Decimal): Capital allocated for the portfolio.
    """

    def __init__(self, capital):

        """
        Costructor method.

        Args:
            capital (int, float, str, decimal.Decimal): Capital allocated for the portfolio.
        """
        
        PortfolioBaseClass.__init__(self, capital = capital)
        

    def set_allocation(self, session, name, df):

        """
        Return a list of allocations (alchemist_lib.database.ptf_allocation.PtfAllocation) based on the weight of every asset.

        Args:
            session (sqlalchemy.orm.session.Session): Connection to the database.
            name (str): Name of the trading system.
            df (pandas.DataFrame): A dataframe with the following columns:
                * asset (alchemist_lib.database.asset.Asset): Must be the index.
                * weight (decimal.Decimal): The weight of the specified asset in the portfolio. The sum of all weights in the dataframe must be near 1.

        Return:
            allocs (list[PtfAllocation]): List of allocations (ideal portfolio).
        """
        
        assert df.index.name == "asset", "The set_allocation function must receive a dataframe with the column 'asset' as index."
        assert "weight" in df.columns, "The set_allocation function must receive a dataframe with a column called 'weight'."

        my_df = df.copy()
        last_price = datafeed.get_last_price(assets = my_df.index.values)

        my_df["amount"] = np.nan
        my_df["base_currency_amount"] = np.nan
        for asset, weight in zip(my_df.index.values, my_df["weight"]):
            base_currency_amount = Decimal(weight) * Decimal(self.capital)
            my_df.loc[asset, "base_currency_amount"] = base_currency_amount

            try:
                if asset.instrument.instrument_type != "cryptocurrency":
                    my_df.loc[asset, "amount"] = Decimal(int(base_currency_amount) / last_price.loc[asset, "last_price"])
                else:
                    my_df.loc[asset, "amount"] = Decimal(base_currency_amount / last_price.loc[asset, "last_price"])
            except DivisionByZero:
                my_df.loc[asset, "amount"] = Decimal(0)
                
                
        my_df.drop(labels = ["weight"], axis = 1, inplace = True)
        my_df["name"] = name

        allocs = PtfAllocation.from_dataframe(session = session, df = my_df)
        return allocs
