from sqlalchemy import Column, Integer, String

from . import Base



class Timetable(Base):

    """
    Map class for table timetable.

        - **timetable_id**: Integer, primary_key.
        - **open_hour**: Integer, not null.
        - **open_minute**: Integer, not null.
        - **close_hour**: Integer, not null.
        - **close_minute**: Integer, not null.
        - **timezone**: String(100), not null.
    """

    __tablename__ = "timetable"

    timetable_id = Column(Integer, primary_key = True)
    open_hour = Column(Integer, nullable = False)
    open_minute = Column(Integer, nullable = False)
    close_hour = Column(Integer, nullable = False)
    close_minute = Column(Integer, nullable = False)
    timezone = Column(String(100), nullable = False)


    def __init__(self, open_hour, open_minute, close_hour, close_minute, timezone):

        """
        Costructor method.

        Args:
            - open_hour (int): Opening hour.
            - open_minute (int): Opening minute.
            - close_hour (int): Closing hour.
            - close_minute (int): Closing minute.
            - timezone (str): Timezone name. Example: US/Eastern
        """

        self.open_hour = open_hour
        self.open_minute = open_minute
        self.close_hour = close_hour
        self.close_minute = close_minute
        self.timezone = timezone


    def __repr__(self):
        return "<Timetable(open_hour={}, open_minute={}, close_hour={}, close_minute={}, timezone={})>".format(self.open_hour,
                                                                                                               self.open_minute,
                                                                                                               self.close_hour,
                                                                                                               self.close_minute,
                                                                                                               self.timezone
                                                                                                               )

