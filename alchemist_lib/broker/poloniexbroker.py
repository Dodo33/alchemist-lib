from poloniex import Poloniex, PoloniexError

import datetime as dt

from .broker import BrokerBaseClass

from ..database.executed_order import ExecutedOrder

from decimal import Decimal

import logging



class PoloniexBroker(BrokerBaseClass):

    """
    Inherits from alchemist_lib.broker.broker.BrokerBaseClass.

    Website: https://poloniex.com/

    Api documentation: https://poloniex.com/support/api/

    Api wrapper: https://github.com/s4w3d0ff/python-poloniex

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
        polo (poloniex.Poloniex): Communication object.
    """
    
    def __init__(self, api_key = None, secret_key = None):

        """
        Costructor method.

        Args:
            api_key (str): The api key provided by Poloniex.
            secret_key (str): The secret key provided by Poloniex.

        Note:
            https://poloniex.com/apiKeys
            https://cryptocatbot.com/api-key-activation-exchanges/
        """
        
        BrokerBaseClass.__init__(self)
        self.polo = Poloniex(key = api_key, secret = secret_key)
	
		
    def get_best_rate(self, asset, amount, field):

        """
        Poloniex doesn't allow to place market orders so we need to get the best bid/ask price for every order.

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset we want to exchange for BTC.
            amount (decimal.Decimal): The amount we want to exchange.
            field (str): Must be "ask" or "bid".

        Return:
            price (decimal.Decimal): The best bid/ask, executing an order at this price is like execute a market order. If the book is too thin the return value is 0.
        """

        amount = abs(amount)
        pair = "BTC_{}".format(asset.ticker)
        book = self.polo.returnOrderBook(currencyPair = pair, depth = 20)
        values = book["{}s".format(field)]
        
        orders_sum = Decimal(0)
        for book_item in values:
            orders_sum += Decimal(book_item[1])
            if orders_sum > amount:
                return Decimal(book_item[0])
        
        return Decimal(0)
				
	
    def place_order(self, asset, amount, order_type):

        """
        Places an order for a specific asset on Poloniex.

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset we want exchange for BTC.
            amount (decimal.Decimal): The amount we want to exchange.
            order_type (str): Type of order.

        Return:
            order_id (int): The order identifier, if some error occurs returns -1.
        """
        
        pair = "BTC_{}".format(asset.ticker)

        if amount > 0:
            field = "ask"
            operation = "buy"
        else:
            field = "bid"
            operation = "sell"
            
        if order_type == "MKT":
            rate = self.get_best_rate(asset = asset, amount = abs(amount), field = field)
        else:
            logging.critical("Unknown order type. NotImplemented raised.")
            raise NotImplemented("Unknown order type. NotImplemented raised.")

        logging.debug("Order: Pair: {}. Amount: {}. Operation: {}".format(pair, amount, operation))

        try:
            if operation == "buy":
                order_dict = self.polo.buy(currencyPair = pair, rate = rate, amount = amount)
            else:
                order_dict = self.polo.sell(currencyPair = pair, rate = rate, amount = abs(amount))
            order_id = int(order_dict["orderNumber"])

            order = ExecutedOrder(order_id = order_id,
                                  order_datetime = dt.datetime.utcnow(),
                                  ticker = asset.ticker,
                                  instrument_id = asset.instrument_id,
                                  amount = amount,
                                  operation = operation,
                                  order_type = order_type,
                                  broker_name = "poloniex",
                                  exchange_name = "poloniex"
                                  )

            logging.info("{} order placed for {}. Amount: {}. Order id: {}.".format(operation.upper(), asset.ticker, amount, order_id))
            print("{} order placed for {}. Amount: {}. Order id: {}.".format(operation.upper(), asset.ticker, amount, order_id))
            
            self.session.add(order)
            self.session.commit()
        
        except PoloniexError:
            logging.debug("Order failed for {}.".format(asset.ticker))
            order_id = -1

        return order_id

    
			
			
			
			
			
			
			
			
		
            
