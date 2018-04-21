from sqlalchemy import Column, String

from . import Base



class Broker(Base):

    """
    Map class for table broker.

        - **broker_name**: String(150), primary_key.
        - **website**: String(500), null.
    """
    
    __tablename__ = "broker"

    broker_name = Column(String(150), primary_key = True)
    website = Column(String(500), nullable = True)


    def __init__(self, broker_name, website = None):

        """
        Costructor method.

        Args:
            broker_name (str): Name of the broker.
            website (str, optional): Site of the broker.
        """
        
        self.broker_name = broker_name
        self.website = website


    def __repr__(self):
        return "<Broker(broker_name={}, website={}>".format(self.broker_name, self.website)
