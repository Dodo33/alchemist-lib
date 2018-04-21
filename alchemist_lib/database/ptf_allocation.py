import pandas as pd

from sqlalchemy import Float, String, ForeignKey, Integer, Column, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from .ts import Ts

from . import Base



class PtfAllocation(Base):

    """
    Map class for table ptf_allocation.

        - **allocation_id**: Integer, primary_key.
        - **amount**: Float(20, 8), not null.
        - **base_currency_amount**: Float(20, 8), not null.
        - **ts_name**: String(150), not null, foreign_key(ts.ts_name).
        - **ticker**: String(16), not null, foreign_key(asset.ticker).
        - **instrument_id**: Integer, not null, foreign_key(asset.instrument_id).

    Relationship:
        - **asset**: Asset instance. (Many-to-One)
        - **ts**: TradingSystem instance. (Many-to-One)
    """
    
    __tablename__ = "ptf_allocation"
    __table_args__ = (ForeignKeyConstraint(["ticker", "instrument_id"], ["asset.ticker", "asset.instrument_id"], ondelete = "cascade"), )


    allocation_id = Column(Integer, primary_key = True)
    amount = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = False)
    base_currency_amount = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = False)
    ts_name = Column(String(150), ForeignKey("ts.ts_name"), nullable = False)
    ticker = Column(String(16), nullable = False)
    instrument_id = Column(Integer, nullable = False)

    asset = relationship("Asset")
    ts = relationship("Ts")
    

    def __init__(self, amount, base_currency_amount, ts_name, ticker, instrument_id):

        """
        Costructor method.

        Args:
            ticker (str): Ticker code of the asset.
            instrument_id (int): Integer that identify tha type of financial instrument.
            amount (decimal.Decimal): Amount of the asset.
            base_currency_amount (decimal.Decimal): Amount of the base currency used to buy the amount of asset.
            ts_name (str): Name of the trading system that manages this allocation.
        """
        
        self.amount = amount
        self.base_currency_amount = base_currency_amount
        self.ts_name = ts_name
        self.ticker = ticker
        self.instrument_id = instrument_id
        

    def __repr__(self):
        return "<PtfAllocation(amount={}, base_currency_amount={}, ticker={}, instrument_id={}, ts_name={})>".format(self.amount,
                                                                                                                      self.base_currency_amount,
                                                                                                                      self.ticker,
                                                                                                                      self.instrument_id,
                                                                                                                      self.ts_name
                                                                                                                      ) 


    def __str__(self):
        return "{} {}".format(round(self.amount, 8), self.ticker)
    

    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"amount" : self.amount,
                "base_currency_amount" : self.base_currency_amount,
                "ts_name" : self.ts_name,
                "ticker" : self.ticker,
                "instrument_id" : self.instrument_id
                }
    

    def deepcopy(self):

        """
        Notes:
            https://www.python-course.eu/deep_copy.php
            https://docs.python.org/2/library/copy.html
        """
        
        cls = self.__class__
        result = cls.__new__(cls)

        result = PtfAllocation(ticker = self.ticker,
                               instrument_id = self.instrument_id,
                               amount = self.amount,
                               base_currency_amount = self.base_currency_amount,
                               ts_name = self.ts_name
                               )
        return result
        
        
    
    def __eq__(self, other):
        
        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.to_dict() == other.to_dict()
        return False


    def from_dataframe(session, df):

        """
        Turn a pandas.DataFrame into a list of PtfAllocation.

        Args:
            - session (sqlalchemy.orm.session): The session that will be used to retrieve data from the database.
            - df (pandas.DataFrame): Dataframe that will be turned into a list of PtfAllocation.

        Returns:
            ptf_allocations (list[PtfAllocation]): A list of PtfAllocation instances.

        Note:
            It's a static method.
        """
        
        assert isinstance(df, pd.DataFrame), "The 'df' arg must be a dataframe (pandas.DataFrame)."
        assert "amount" in df.columns, "The 'df' arg must has a column called 'amount'."
        assert "name" in df.columns, "The 'df' arg must has a column called 'name'."
        assert "base_currency_amount" in df.columns, "The 'df' arg must has a column called 'base_currency_amount'."


        ptf_allocations = []
        for index, row in df.iterrows():
            alloc = PtfAllocation(amount = row["amount"],
                                  base_currency_amount = row["base_currency_amount"],
                                  ticker = index.ticker,
                                  instrument_id = index.instrument_id,
                                  ts_name = row["name"])
            alloc.asset = index
            alloc.ts = session.query(Ts).filter(Ts.ts_name == row["name"]).one()
        
            ptf_allocations.append(alloc)
            
        return ptf_allocations


    
