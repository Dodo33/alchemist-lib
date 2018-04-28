from sqlalchemy import String, ForeignKey, DateTime, Float, Integer, Column, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base



class Ohlcv(Base):

    """
    Map class for table ohlcv.

        - **ohlcv_id**: Integer, primary key.
        - **ohlcv_datetime**: DateTime.
        - **timeframe_id**: String(4), not null.
        - **ticker**: String(16), not null, foreign_key(asset.ticker).
        - **instrument_id**: Integer, not null, foreign_key(asset.instrument_id).
        - **open**: Float(20, 8), not null.
        - **high**: Float(20, 8), not null.
        - **low**: Float(20, 8), not null.
        - **close**: Float(20, 8), not null.
        - **volume**: Float(20, 8), not null.

    Relationship:
        - **asset**: Asset instance. (Many-to-One)
    """
    
    __tablename__ = "ohlcv"
    __table_args__ = (ForeignKeyConstraint(["ticker", "instrument_id"], ["asset.ticker", "asset.instrument_id"], ondelete = "cascade"), UniqueConstraint("ohlcv_datetime",
                                                                                                                                                         "timeframe_id",
                                                                                                                                                         "ticker",
                                                                                                                                                         "instrument_id"), )

    ohlcv_id = Column(Integer, primary_key = True)
    ohlcv_datetime = Column(DateTime)
    timeframe_id = Column(String(4), nullable = False)
    ticker = Column(String(16), nullable = False)
    instrument_id = Column(Integer, nullable = False)
    
    open = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    high = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    low = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    close = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    volume = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    
    asset = relationship("Asset")
    

    def __init__(self, ohlcv_datetime, timeframe_id, open, high, low, close, volume, ticker, instrument_id):

        """
        Costructor method.

        Args:
            - ohlcv_datetime (datetime.datetime): Close datetime of the candle.
            - timeframe_id (str): Timeframe identifier.
            - ticker (str): Ticker code of the asset.
            - instrument_id (int): Integer number that identify the financial instrument of the asset.
            - open (decimal.Decimal): Open price.
            - high (decimal.Decimal): High price.
            - low (decimal.Decimal): Low price.
            - close (decimal.Decimal): Close price.
            - volume (decimal.Decimal): Volume of assets exchanged in the timeframe.
        """
        
        self.ohlcv_datetime = ohlcv_datetime
        self.timeframe_id = timeframe_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.ticker = ticker
        self.instrument_id = instrument_id


    def __init__(self):

        """
        Costructor method without args.
        """
        
        pass
    

    def __repr__(self):
        return "<Ohlcv(ohlcv_datetime={}, timeframe_id={}, open={}, high={}, low={}, close={}, volume={}, ticker={}, instrument_id={})>".format(self.ohlcv_datetime,
                                                                                                                                    self.timeframe_id,
                                                                                                                                    self.open,
                                                                                                                                    self.high,
                                                                                                                                    self.low,
                                                                                                                                    self.close,
                                                                                                                                    self.volume,
                                                                                                                                    self.ticker,
                                                                                                                                    self.instrument_id
                                                                                                                                    )

    
    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"ohlcv_datetime" : self.ohlcv_datetime,
                "timeframe_id" : self.timeframe_id,
                "open" : self.open,
                "high" : self.high,
                "low" : self.low,
                "close" : self.close,
                "volume" : self.volume,
                "ticker" : self.ticker,
                "instrument_id" : self.instrument_id
                }
    
    
    def __eq__(self, other):
        
        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.to_dict() == other.to_dict()
        return NotImplemented


    def __hash__(self):
        
        """
        Overrides the default implementation.
        """
        
        return hash(tuple(sorted(self.to_dict().items())))
