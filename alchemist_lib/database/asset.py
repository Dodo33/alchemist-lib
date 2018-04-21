from sqlalchemy import Table, String, ForeignKey, Integer, Column, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref

from . import Base



asset_exchange_association = Table(
    "asset_exchange", Base.metadata,
    Column("ticker", String(16), primary_key = True),
    Column("instrument_id", Integer, primary_key = True),
    Column("exchange_name", String(150), ForeignKey("exchange.exchange_name"), primary_key = True),
    ForeignKeyConstraint(["ticker", "instrument_id"], ["asset.ticker", "asset.instrument_id"], ondelete = "cascade")
)


class Asset(Base):

    """
    Map class for table asset.

        - **ticker**: String(16), primary_key.
        - **instrument_id**: Integer, primary_key, foreign_key(instrument.instrument_id).
        - **name**: String(150), null.

    Relationships:
    
        - **exchanges**: List of Exchange instances. (Many-to-Many)
        - **instrument**: Instrument instance. (One-to-Many)

    Note:
        https://rszalski.github.io/magicmethods/
    
    """
    
    __tablename__ = "asset"

    ticker = Column(String(16), primary_key = True)
    instrument_id = Column(Integer, ForeignKey("instrument.instrument_id", ondelete = "cascade"), primary_key = True)
    name = Column(String(150), nullable = True)

    exchanges = relationship("Exchange", secondary = asset_exchange_association)
    instrument = relationship("Instrument")
    

    def __init__(self, ticker, instrument_id, name = None):
        
        """
        Costructor method.

        Args:
            ticker (str): Ticker code of the asset.
            instrument_id (int): Integer that identify tha type of financial instrument.
            name (int, optional): Long name of the asset.
        """
        
        self.ticker = ticker
        self.instrument_id = instrument_id
        self.name = name


    def __repr__(self):
        return "<Asset(ticker={}, instrument_id={}, name={})>".format(self.ticker,
                                                                      self.instrument_id,
                                                                      self.name
                                                                     )

    
    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"ticker" : self.ticker,
                "instrument_id" : self.instrument_id,
                "name" : self.name
                }


    def __eq__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) == (other.ticker, other.instrument_id))
        return NotImplemented


    def __ne__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) != (other.ticker, other.instrument_id))
        return NotImplemented


    def __lt__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) < (other.ticker, other.instrument_id))
        return NotImplemented


    def __le__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) <= (other.ticker, other.instrument_id))
        return NotImplemented


    def __gt__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) > (other.ticker, other.instrument_id))
        return NotImplemented


    def __ge__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return ((self.ticker, self.instrument_id) >= (other.ticker, other.instrument_id))
        return NotImplemented


    def __hash__(self):

        """
        Overrides the default implementation.
        """
        
        return hash(tuple(sorted(self.to_dict().items())))








    
            
            
