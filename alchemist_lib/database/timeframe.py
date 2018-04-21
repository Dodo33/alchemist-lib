from sqlalchemy import Column, String

from . import Base



class Timeframe(Base):

    """
    Map class for table timeframe.

        - **timeframe_id**: String(4), primary_key.
        - **description**: String(150), null.
    """

    __tablename__ = "timeframe"

    timeframe_id = Column(String(4), primary_key = True)
    description = Column(String(150), nullable = True)


    def __init__(self, timeframe_id, description):

        """
        Costructor method.

        Args:
            - timeframe_id (str): String that identify the timeframe. (minutes = M, hours = H, days = D).
            - description (str): Timeframe in english words. Example: 15M = fifteen minutes.
        """
        
        self.timeframe_id = timeframe_id
        self.description = description
        
    
    def __repr__(self):
        return "<Timeframe(timeframe_id={}, description={})>".format(self.timeframe_id, self.description)
