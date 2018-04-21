from .poloniexexchange import PoloniexExchange
from .bittrexexchange import BittrexExchange

from ..database.asset import Asset
from ..database.exchange import Exchange

from .. import populate

from .. import utils



def get_exchanges_dict():

    """
    Remember to change this method every time you add a module.

    Return:
        dsd (dict): Returns a dictionary. The key must be the name of the exchange in the database and the value must be an instance of the module charged to collect data.
    """
    
    exchs = {"poloniex" : PoloniexExchange(),
             "bittrex" : BittrexExchange()
            }
    
    return exchs


def are_tradable(assets, exchange_name):

    """
    Removes not tradable asset from the list.

    Args:
        assets (alchemist_lib.database.asset.Asset, list[Asset]): List of assets to filter.
        exchange_name (str): The name of the exchange as is saved in the database.

    Return:
        universe (list[Asset]): Returns the same list of assets passed as arg without not tradable assets. If exchange_name is not correct the return is an empty list.
    """

    assets = utils.to_list(assets)

    exchs = get_exchanges_dict()

    if exchange_name in list(exchs.keys()):
        exch = exchs[exchange_name]
        universe = exch.are_tradable(assets = assets)
    
        return universe

    return []


def get_assets(session, exchange_name):

    """
    Returns all assets traded in a specified exchange.

    Args:
        session (sqlalchemy.orm.session.Session): Database connection.
        exchange_name (str): Name of the exchange.

    Return:
        universe (list[alchemist_lib.database.asset.Asset]): List of Asset instances.
    """
    
    exchange_name = exchange_name.lower()
    available_exchanges = session.query(Exchange).all()
    assert exchange_name in [exchange.exchange_name for exchange in available_exchanges], "Unknown exchange name."
    
    populate.update_asset_list(session = session, exchange_name = exchange_name)
    
    universe = session.query(Asset).join(Exchange, Asset.exchanges).filter(Exchange.exchange_name == exchange_name).all()
    universe = are_tradable(assets = universe, exchange_name = exchange_name)

    return universe





















    
