from ..database import Session

from .poloniexpopulate import PoloniexPopulate
from .bittrexpopulate import BittrexPopulate
from .saver import Saver



def get_populate_dict(saver):

    """
    Remember to change this method every time you add a module.

    Args:
        saver (alchemist_lib.populate.saver.Saver): Instance of the saver class.

    Return:
        all_pop (dict): Return a dictionary. The key must be the name of the data source in the database and the value must be an instance of the module charged to populate the database.
    """
    
    all_pop = {"poloniex" : PoloniexPopulate(saver = saver),
               "bittrex" : BittrexPopulate(saver = saver)
               }
    return all_pop
    

def populate_all(session):

    """
    Populate the database with every populate class.

    Args:
        session (sqlalchemy.orm.session.Session): Database connection.
    """
    
    saver = Saver(session = session)

    pops = get_populate_dict(saver = saver)
    
    for name, instance in pops.items():
        print(name, " OK!")
        instance.populate()
	

def update_asset_list(session, exchange_name = None):

    """
    Populate the tradable assets for every exchange.

    Args:
        session (sqlalchemy.orm.session.Session): Database connection.
        exchange_name (str, optional): Name of the exchange. Default is None. If None update the list for every exchange in the database.
    """
    
    saver = Saver(session = session)

    pops = get_populate_dict(saver = saver)

    if exchange_name != None:
        pop = pops[exchange_name]
        pop.update_asset_list()
    else:
        for name, instance in pops.items():    
            instance.update_asset_list()

    
