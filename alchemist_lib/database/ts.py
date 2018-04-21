from sqlalchemy import String, Float, DateTime, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship

from . import Base

import datetime as dt



class Ts(Base):
    
    """
    Map class for table ts.

        - **ts_name**: String(150), primary_key.
        - **datetime_added**: DateTime, not null.
        - **aum**: Float(20, 8), not null.
        - **ptf_type**: String(150), not null.
    """
    
    __tablename__ = "ts"

    ts_name = Column(String(150), primary_key = True)
    datetime_added = Column(DateTime, nullable = False)
    aum = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = False)
    ptf_type = Column(String(150), nullable = False)


    def __init__(self, ts_name, aum, ptf_type, datetime_added = dt.datetime.now()):

        """
        Costructor method.

        Args:
            ts_name (str): Name of the trading system.
            datetime_added (datetime.datetime, optional): Last date and time when the trading system was initialized. Default is the moment of initialization in UTC format.
            aum (decimal.Decimal): The value of assets under management of the trading system.
            ptf_type (str): String that identify the type of the portfolio.
            
        """
        
        self.ts_name = ts_name
        self.datetime_added = datetime_added
        self.aum = aum
        self.ptf_type = ptf_type


    def __repr__(self):
        return "<TradingSystem(ts_name={}, datetime_added={}, aum={}, ptf_type={})>".format(self.ts_name,
                                                                                            self.datetime_added,
                                                                                            self.aum,
                                                                                            self.ptf_type
                                                                                            )

    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"ts_name" : self.ts_name,
                "datetime_added" : self.datetime_added,
                "aum" : self.aum,
                "ptf_type" : self.ptf_type
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
