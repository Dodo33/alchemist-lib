import sys

import os

import argparse

import configparser



def main():
    args = sys.argv
    
    parser = argparse.ArgumentParser()
    parser.add_argument("populate", type = str, default = "localhost", help = "Populate the database.")
    parser.add_argument("-l", "--hostname", type = str, default = "localhost", help = "Hostname of computer where the DBMS is located.(default = localhost)")
    parser.add_argument("-u", "--user", type = str, default = "admin", help = "DBMS username.")
    parser.add_argument("-p", "--pass", type = str, default="root", help="DBMS password.")
    parser.add_argument("-d", "--db", type = str, default = "alchemist_lib", help = "Database name.")
    
    parsed_args = parser.parse_args()

    #path = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.dirname(__file__)
    
    config = configparser.ConfigParser()
    
    if parsed_args.populate == "populate":
        config["DATABASE"] = {}
        for key, value in parsed_args.__dict__.items():
            config["DATABASE"][key] = str(value)

        with open(path + "/config.ini", "w") as configfile:
            config.write(configfile)

        from . import database
        from .database import Engine, Session
        from .database.asset import Asset
        from .database.aum_history import AumHistory
        from .database.broker import Broker
        from .database.price_data_source import PriceDataSource
        from .database.exchange import Exchange
        from .database.instrument import Instrument
        from .database.ohlcv import Ohlcv
        from .database.ptf_allocation import PtfAllocation
        from .database.timeframe import Timeframe
        from .database.timetable import Timetable
        from .database.ts import Ts
        from .database.executed_order import ExecutedOrder

        from . import populate
        
        
        database.Base.metadata.create_all(database.Engine)
        
        #https://stackoverflow.com/questions/10455547/delimiter-creating-a-trigger-in-sqlalchemy
        trigger_text = "CREATE TRIGGER aum_history_saver \
                        BEFORE UPDATE ON ts \
                        FOR EACH ROW \
                        BEGIN \
                        INSERT INTO aum_history(aum_datetime, aum, ts_name) VALUES (CURRENT_TIMESTAMP, NEW.aum, NEW.ts_name); \
                        END"
        
        Engine.execute("DROP TRIGGER IF EXISTS aum_history_saver")
        Engine.execute(trigger_text)

        session = Session()
        populate.populate_all(session = session)
        session.close()

        print("Database populated.")
        
    else:
        print("Unknown command.")


if __name__ == "__main__":
    main(args)
