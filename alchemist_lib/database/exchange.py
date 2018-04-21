from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import Base



exchange_broker_association = Table(
    "exchange_broker", Base.metadata,
    Column("exchange_name", String(150), ForeignKey("exchange.exchange_name"), primary_key = True),
    Column("broker_name", String(150), ForeignKey("broker.broker_name"), primary_key = True)
)


class Exchange(Base):
    
    """
    Map class for table exchange.

        - **exchange_name**: String(150), primary_key.
        - **website**: String(500), null.
        - **timetable_id**: Integer, null, foreign_key(timetable.timetable_id).
        - **price_data_source_name**: String(150), null, foreign_key(price_data_source.price_data_source_name).

    Relationships:
        - **price_data_source**: PriceDataSource instance. (One-to-Many)
        - **timetable**: Timetable instance. (One-to-Many)
        - **brokers**: List of Broker instances. (Many-to-Many)
    """
    
    __tablename__ = "exchange"

    exchange_name = Column(String(150), primary_key = True)
    website = Column(String(500), nullable = True)
    timetable_id = Column(Integer, ForeignKey("timetable.timetable_id"), nullable = True)
    price_data_source_name = Column(String(150), ForeignKey("price_data_source.price_data_source_name"), nullable = True)
    
    price_data_source = relationship("PriceDataSource")
    timetable = relationship("Timetable")
    brokers = relationship("Broker", secondary = exchange_broker_association)
    

    def __init__(self, exchange_name, website = None, timetable_id = None, price_data_source_name = None):

        """
        Costructor method.

        Args:
            exchange_name (str): Name (or acronym) of the exchange.
            website (str, optional): Site of the exchange.
            timetable_id (int, optional): Timetable identification of trading hours. None if the market never ends.
            price_data_source_name (int, optional): Name that identify the data source for OHLCV and last_price data.
        """
        
        self.exchange_name = exchange_name
        self.website = website
        self.timetable_id = timetable_id
        self.price_data_source_name = price_data_source_name

    
    def __repr__(self):
        return "<Exchange(exchange_name={}, website={}, timetable_id={}, price_data_source_name={})>".format(self.exchange_name,
                                                                                                             self.website,
                                                                                                             self.timetable_id,
                                                                                                             self.price_data_source_name)

