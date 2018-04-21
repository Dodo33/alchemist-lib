from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import Base



price_data_source_timeframe_association = Table(
    "price_data_source_timeframe", Base.metadata,
    Column("price_data_source_name", String(150), ForeignKey("price_data_source.price_data_source_name"), primary_key = True),
    Column("timeframe_id", String(4), ForeignKey("timeframe.timeframe_id"), primary_key = True)
)


class PriceDataSource(Base):

    """
    Map class for data_source.

        - **price_data_source_name**: String(150), not null, primary_key.
        - **website**: String(500), null.

    Relationships:
        - **available_timeframes**: List of Timeframe instances. (Many-to-Many).
    """

    __tablename__ = "price_data_source"

    price_data_source_name = Column(String(150), nullable = False, primary_key = True)
    website = Column(String(500), nullable = True)

    available_timeframes = relationship("Timeframe", secondary = price_data_source_timeframe_association)
    

    def __init__(self, price_data_source_name, website = None):

        """
        Costructor mathod.

        Args:
            - price_data_source_name (str): Name of the source of informations.
            - website (str, optional): Site of the source of informations.
        """
        
        self.price_data_source_name = price_data_source_name
        self.website = website


    def __repr__(self):
        return "<DataSource(price_data_source_name={}, website={})>".format(self.price_data_source_name, self.website)
