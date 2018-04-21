from sqlalchemy import DateTime, String, ForeignKey, Integer, Column, Float
from sqlalchemy.orm import relationship

from . import Base



class AumHistory(Base):

    """
    Map class for table AumHistory.

        - **aum_id**: Integer, primary_key.
        - **aum_datetime**: DateTime, not null.
        - **aum**: Float(20, 8), not null.
        - **ts_name**: String(150), not null, foreign_key(ts.ts_name).

    Relationships:
    
        - **ts**: TradingSystem instance. (Many-to-One)
    """
    
    __tablename__ = "aum_history"

    aum_id = Column(Integer, primary_key = True)
    aum_datetime = Column(DateTime, nullable = False)
    aum = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = False)
    ts_name = Column(String(150), ForeignKey("ts.ts_name"), nullable = False)

    ts = relationship("Ts")


    def __repr__(self):
        return "<AumHistory(datetime={}, aum={}, ts={})>".format(self.aum_datetime,
                                                                 self.aum,
                                                                 self.ts_name
                                                                 )
