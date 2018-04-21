from bittrex.bittrex import Bittrex, API_V1_1, SELL_ORDERBOOK, BUY_ORDERBOOK

from decimal import Decimal

import datetime as dt

from .broker import BrokerBaseClass

from ..exchange import BittrexExchange

from ..database.executed_order import ExecutedOrder

import logging



class BittrexBroker(BrokerBaseClass):

    """
    Inherits from alchemist_lib.broker.broker.BrokerBaseClass.

    Website: https://bittrex.com/

    Api documentation: https://bittrex.com/Home/Api

    Api wrapper: https://github.com/ericsomdahl/python-bittrex

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection.
        bittrex (bittrex.bittrex.Bittrex): Communication object.
    """
    
    def __init__(self, api_key = None, secret_key = None):

        """
        Costructor method.

        Args:
            api_key (str): The api key provided by Bittrex.
            secret_key (str): The secret key provided by Bittrex.

        Note:
            https://bittrex.com/Manage#sectionApi
            https://cryptocatbot.com/api-key-activation-exchanges/
        """
        
        BrokerBaseClass.__init__(self)
        self.bittrex = Bittrex(api_key = api_key, api_secret = secret_key, api_version = API_V1_1)


    def get_best_rate(self, asset, amount, field):

        """
        Bittrex doesn't allow to place market orders submitted via API so we need to get the best bid/ask price for every order.

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset we want to exchange for BTC or vice versa.
            amount (decimal.Decimal): The amount we want to exchange.
            field (str): Must be "ask" or "bid".

        Return:
            price (decimal.Decimal): The best bid/ask, executing an order at this price is like submit a market order. If the book is too thin the return value is 0.
        """

        amount = abs(amount)
        pair = "BTC-{}".format(asset.ticker)
        if field == "ask":
            book = self.bittrex.get_orderbook(market = pair, depth_type = SELL_ORDERBOOK)
            if book["success"] == False or book["result"] == None:
                logging.debug("Bittrex api result is None or success is False. get_best_rate() method. Asset: {}".format(asset.ticker))
                return Decimal(0)
            
        else:
            book = self.bittrex.get_orderbook(market = pair, depth_type = BUY_ORDERBOOK)
            if book["success"] == False or book["result"] == None:
                logging.debug("Bittrex api result is None or success is False. get_best_rate() method. Asset: {}".format(asset.ticker))
                return Decimal(0)
            
        values = book["result"]
        
        orders_sum = Decimal(0)
        for book_item in values:
            orders_sum += Decimal(book_item["Quantity"])
            if orders_sum > amount:
                return Decimal(book_item["Rate"])
        
        return Decimal(0)
    
	
    def place_order(self, asset, amount, order_type):

        """
        Places an order for a specific asset on Bittrex.

        Args:
            asset (alchemist_lib.database.asset.Asset): The asset we want exchange for BTC.
            amount (decimal.Decimal): The amount we want to exchange.
            order_type (str): Type of order.

        Return:
            order_id (str, int): Order identifier, if some errors occur it returns int(-1).
        """
        
        pair = "BTC-{}".format(asset.ticker)
        
        min_order_size = BittrexExchange().get_min_order_size(asset = asset)
        logging.debug("Min order size for {} is {}".format(asset, min_order_size))
        
        if amount > min_order_size:
            field = "ask"
            operation = "buy"
        elif amount < (min_order_size * (-1)):
            field = "bid"
            operation = "sell"
        else:
            return -1

        if order_type == "MKT":
            rate = self.get_best_rate(asset = asset, amount = abs(amount), field = field)
        else:
            logging.critical("Unknown order type. NotImplemented raised.")
            raise NotImplemented("Unknown order type. NotImplemented raised.")

        logging.debug("Order: Pair: {}. Amount: {}. Operation: {}".format(pair, amount, operation))
        
        if operation == "buy":
            order_return_dict = self.bittrex.buy_limit(market = pair, rate = rate, quantity = amount)
        else:
            order_return_dict = self.bittrex.sell_limit(market = pair, rate = rate, quantity = abs(amount))
        
        if order_return_dict["result"] == None:
            logging.warning("Bittrex api result is None or success is False. place_order() method. Order id will be -1. Asset: {}".format(asset.ticker))
            return -1

        order_id = str(order_return_dict["result"]["uuid"])

        logging.info("{} order placed for {}. Amount: {}. Order id: {}.".format(operation.upper(), asset.ticker, amount, order_id))
        print("{} order placed for {}. Amount: {}. Order id: {}.".format(operation.upper(), asset.ticker, amount, order_id))

        order = ExecutedOrder(order_id = order_id,
                              order_datetime = dt.datetime.utcnow(),
                              ticker = asset.ticker,
                              instrument_id = asset.instrument_id,
                              amount = amount,
                              operation = operation,
                              order_type = order_type,
                              broker_name = "bittrex",
                              exchange_name = "bittrex"
                              )
        
        self.session.add(order)
        self.session.commit()
                
        return order_id
			
			
			
			
			
			
			
