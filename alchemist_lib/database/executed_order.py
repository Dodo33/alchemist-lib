import datetime as dt

from sqlalchemy import DateTime, String, ForeignKey, Integer, Column, Float, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from . import Base



class ExecutedOrder(Base):

    """
    Map class for table executed_order.

        - **order_datetime**: DateTime, primary_key.
        - **ticker**: String(16), primary_key.
        - **instrument_id**: Integer, primary_key.
	- **order_id**: String(150), not null.
        - **exchange_name**: String(150), not null, foreign_key(exchange.exchange_name).
        - **broker_name**: String(150), not null, foreign_key(broker.broker_name)
        - **order_type**: String(3), not null.
        - **operation**: String(4), not null.
        - **amount**: Float(20, 8), not null.
        - **price**: Float(20, 8), null.
        - **paid_fee**: Float(20, 8), null.

    Relationships:
    
        - **exchange**: List of Exchange instances. (One-to-Many)
        - **asset**: Asset instance. (One-to-Many)
        - **broker**: Broker instance. (One-to-Many)
    
    """
    
    __tablename__ = "executed_order"
    __table_args__ = (ForeignKeyConstraint(["ticker", "instrument_id"], ["asset.ticker", "asset.instrument_id"], ondelete = "cascade"), )

    order_datetime = Column(DateTime, primary_key = True)
    ticker = Column(String(16), primary_key = True)
    instrument_id = Column(Integer, primary_key = True)
    order_id = Column(String(150), nullable = False)
    exchange_name = Column(String(150), ForeignKey("exchange.exchange_name"), nullable = False)
    broker_name = Column(String(150), ForeignKey("broker.broker_name"), nullable = False)
    order_type = Column(String(3), nullable = False)
    operation = Column(String(4), nullable = False)
    amount = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = False)
    price = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)
    paid_fee = Column(Float(precision = 20, scale = 8, asdecimal = True), nullable = True)

    exchange = relationship("Exchange")
    asset = relationship("Asset")
    broker = relationship("Broker")
    

    def __init__(self, order_id, ticker, instrument_id, exchange_name, broker_name, order_type, operation, amount, price = None, paid_fee = 0, order_datetime = dt.datetime.utcnow()):
        
        """
        Costructor method.

        Args:
	    order_id (str): Order identified, the form depends of the enchange.
            order_datetime (datetime.datetime, optional): When the order is submitted. Default is utcnow().
            ticker (str): Ticker code of the asset.
            instrument_id (int): Integer that identify tha type of financial instrument.
            exchange_name (str): Name of the exchange where the order is executed.
            broker_name (str): Name of the broker that execute the order.
            order_type (str): String that identify the type of order. Market, Limit, ecc.
            operation (str): The type of operation. (buy or sell).
            amount (decimal.Decimal): Order amount.
            price (decimal.Decimal, optional): Price of order execution. None if order_type is market.
            paid_fee (decimal.Decimal): Fee amount, in the base currency or in the quote one.
        """
        
        self.order_datetime = order_datetime
        self.order_id = order_id
        self.ticker = ticker
        self.instrument_id = instrument_id
        self.exchange_name = exchange_name
        self.broker_name = broker_name
        self.order_type = order_type
        self.operation = operation
        self.amount = amount
        self.price = price
        self.paid_fee = paid_fee
        

    def __repr__(self):
        return "<ExecutedOrder(order_id = {}, order_datetime={}, ticker={}, instrument_id={}, exchange_name={}, broker_name={}, order_type={}, operation={}, amount={}, price={}, paid_fee={})>".format(self.order_id,
                                                                                                                                                                                                        self.order_datetime,
                                                                                                                                                                                                        self.ticker,
                                                                                                                                                                                                        self.instrument_id,
                                                                                                                                                                                                        self.exchange_name,
                                                                                                                                                                                                        self.broker_name,
                                                                                                                                                                                                        self.order_type,
                                                                                                                                                                                                        self.operation,
                                                                                                                                                                                                        self.amount,
                                                                                                                                                                                                        self.price,
                                                                                                                                                                                                        self.paid_fee)

    
    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"order_id" : self.order_id,
		"order_datetime" : self.order_datetime,
                "ticker" : self.ticker,
                "instrument_id" : self.instrument_id,
                "exchange_name" : self.exchange_name,
                "broker_name" : self.broker_name,
                "order_type" : self.order_type,
                "operation" : self.operation,
                "amount" : self.amount,
                "price" : self.price,
                "paid_fee" : self.paid_fee
                }


            
            

