from abc import ABC, abstractmethod

from ..database.instrument import Instrument
from ..database.ptf_allocation import PtfAllocation

from .. import utils

import logging



class BrokerBaseClass(ABC):

    """
    Abstract class used by broker modules.

    Abstract methods:
        - place_order(allocs, amount, operation, order_type): It has to place an order based on parameters.

    Attributes:
        session (sqlalchemy.orm.session.Session): Database connection. Default is None.
    """
    
    def __init__(self):

        """
        Costructor method.
        """
        
        self.session = None


    def set_session(self, session):

        """
        Setter method.

        Args:
            session (sqlalchemy.orm.session.Session): Database connection.
        """
        
        self.session = session


    @abstractmethod
    def place_order(self, asset, amount, operation, order_type):
        pass


    def execute(self, allocs, ts_name, curr_ptf, orders_type = "MKT"):

        """
        This method will execute orders for all portfolio. Before the SELL orders and after the BUY orders in order to have enought liquidity.

        Args:
            allocs (list[alchemist_lib.database.ptf_allocation.PtfAllocation]): List of allocations to be executed on the market.
            orders_type (str, optional): Type of order. Default is MKT.
            ts_name (str): Name of the trading system.
            curr_ptf (list[alchemist_lib.database.ptf_allocation.PtfAllocation]): List of allocations currently in the portfolio.
        """
        
        allocs = utils.to_list(allocs)

        cryptocurrency_id = self.session.query(Instrument).filter(Instrument.instrument_type == "cryptocurrency").one().instrument_id
        
        btc = PtfAllocation(ticker = "BTC",
                            instrument_id = cryptocurrency_id,
                            amount = 0,
                            base_currency_amount = 0,
                            ts_name = ts_name)

        #https://stackoverflow.com/questions/10665591/how-to-remove-list-elements-in-a-for-loop-in-python
        for alloc in allocs[:]:
            if alloc.ticker == "BTC" and alloc.instrument_id == cryptocurrency_id:
                btc.amount = abs(alloc.base_currency_amount)
                btc.base_currency_amount = abs(alloc.base_currency_amount)
                allocs.remove(alloc)

        new_curr_ptf = []

        logging.debug("Currently in the execute() method.")
        logging.debug("Initial BTC balance: {}".format(btc.base_currency_amount))
        
        for alloc in allocs:
            if alloc.amount < 0:
                order_id = self.place_order(asset = alloc.asset, amount = alloc.amount, order_type = orders_type)

                logging.debug("<SELL> Asset: {} -> {}".format(alloc.asset, order_id))

                if order_id == -1:
                    #If I can't sell it, the amount is the same of the one in curr_ptf.
                    for curr_ptf_alloc in curr_ptf:
                        if curr_ptf_alloc.asset == alloc.asset:
                            new_curr_ptf.append(curr_ptf_alloc.deepcopy())
                else:
                    if alloc.asset in [ptf_alloc.asset for ptf_alloc in curr_ptf]:
                        for ptf_alloc in curr_ptf:
                            if ptf_alloc.asset == alloc.asset:
                                new_curr_ptf_alloc = ptf_alloc.deepcopy()
                                new_curr_ptf_alloc.amount = ptf_alloc.amount - abs(alloc.amount)
                                new_curr_ptf_alloc.base_currency_amount = ptf_alloc.base_currency_amount - abs(alloc.base_currency_amount)
                                
                                new_curr_ptf.append(new_curr_ptf_alloc)
                    else:
                        new_curr_ptf.append(alloc)

                    btc.amount += abs(alloc.base_currency_amount)
                    btc.base_currency_amount += abs(alloc.base_currency_amount)

                    logging.debug("After I've sold {} the BTC balance is {}".format(alloc.asset.ticker, btc.amount))
                    

        for alloc in allocs:
            if alloc.amount > 0:
                order_id = self.place_order(asset = alloc.asset, amount = alloc.amount, order_type = orders_type)
                
                logging.debug("<BUY> Asset: {} -> {}".format(alloc.asset, order_id))
                
                if order_id == -1:
                    if alloc.asset in [ptf_alloc.asset for ptf_alloc in curr_ptf]:
                        for curr_ptf_alloc in curr_ptf:
                            if curr_ptf_alloc.asset == alloc.asset:
                                new_curr_ptf.append(curr_ptf_alloc.deepcopy())
                            
                else:
                    if alloc.asset in [ptf_alloc.asset for ptf_alloc in curr_ptf]:
                        for ptf_alloc in curr_ptf:
                            if ptf_alloc.asset == alloc.asset:
                                new_curr_ptf_alloc = ptf_alloc.deepcopy()
                                new_curr_ptf_alloc.amount = ptf_alloc.amount + alloc.amount
                                new_curr_ptf_alloc.base_currency_amount = ptf_alloc.base_currency_amount + alloc.base_currency_amount
                                
                                new_curr_ptf.append(new_curr_ptf_alloc)
                    else:
                        new_curr_ptf.append(alloc)

                    
                    btc.amount -= alloc.base_currency_amount
                    btc.base_currency_amount -= alloc.base_currency_amount

                    logging.debug("After I've bought {} the BTC balance is {}".format(alloc.asset.ticker, btc.amount))
                    

        logging.debug("BTC balance at the end of execute() is {}".format(btc.amount))

        #Shouldn't go inside the following statetement.
        if btc.amount > 0:
            new_curr_ptf.append(btc)
        
        return new_curr_ptf
                        
                
